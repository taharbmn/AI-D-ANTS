import os
import sys
sys.path.insert(0, 
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
                )
            )
        )
    )
import io
import json
import time
import boto3
import logging
import mimetypes
from typing                  import Dict, List
from app.utils               import get_local_data_dir, load_system_prompt
from app.files.files         import FileReader
from app.models.chat         import MetaDataRequest
from app.endpoints.metadata  import get_metadata
from app.validators.metadata import MetadataValidator, DescriptionValidator
from app.chatproxy import ChatProxyClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TreeStructure:

    @staticmethod
    def save(structure: Dict[str, Dict], destination: str) -> None:
        destination = destination.strip()
        if destination.startswith("local-data://"):
            fullpath = os.path.join(get_local_data_dir(), destination[len("local-data://"):])
            os.makedirs(os.path.dirname(fullpath), exist_ok = True)
            with io.open(fullpath, "w", encoding="utf-8") as f:
                json.dump(structure, f, ensure_ascii = False, indent = 4)
            return (True)
        else:
            raise ValueError("Destination must start with 'local-data://'")
        return (False)

    @staticmethod
    def download_from_s3(bucket_name, local_dir, root="/"):
        s3_client = boto3.client('s3')
        s3_prefix = ""
        if root and root != "/":
            s3_prefix = root
            if not s3_prefix.endswith('/'):
                s3_prefix += '/'
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
            print(f"Created local directory: {local_dir}")

        try:
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix)

            if s3_prefix:
                print(f"Starting download of folder '{s3_prefix}' from bucket '{bucket_name}'...")
            else:
                print(f"Starting download of entire bucket '{bucket_name}'...")

            download_count = 0
            found_files = False
            for page in pages:
                if "Contents" in page:
                    found_files = True
                    for obj in page['Contents']:
                        s3_key = obj['Key']
                        if s3_key.endswith('/'):
                            continue
                        relative_path   = os.path.relpath(s3_key, s3_prefix)
                        local_file_path = os.path.join(local_dir, relative_path)
                        local_file_dir  = os.path.dirname(local_file_path)
                        if not os.path.exists(local_file_dir):
                            os.makedirs(local_file_dir)
                        print(f"  Downloading: {s3_key} -> {local_file_path}")
                        s3_client.download_file(bucket_name, s3_key, local_file_path)
                        download_count += 1
            
            print("-" * 30)
            if not found_files:
                print(f"Warning: No files found in bucket '{bucket_name}' with prefix '{s3_prefix}'.")
                print("Please check if the bucket name and path are correct.")
            else:
                print(f"Download complete. Total files downloaded: {download_count}")

        except Exception as e:
            print(f"An unexpected S3 client error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
    @staticmethod
    def content_type(filename: str) -> str:
        """
        Guesses the MIME type of a file based on its file extension.

        Args:
            file_path (str): The path to the file.

        Returns:
            str: The guessed MIME type (e.g., 'text/plain'), or
                'application/octet-stream' if the type is unknown.
        """
        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = 'text/plain'
        if content_type == "text/plain":
            extension = TreeStructure.get_file_extension(filename)
            if extension == "csv":
                return 'text/csv'
            elif extension == "json":
                return 'application/json'
        return content_type

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get the file extension from a filename.
        Parameters:
            filename (str): The name of the file.
        Returns:
            str: The file extension, or an empty string if no extension is found.
        """
        filename = filename.strip()
        while filename and filename[-1] in ["\\", "/", "."]:
            filename = filename[:-1].strip()
        if not filename:
            return ''
        basename = filename.split("/")[-1].strip()
        if not basename:
            return ''
        if not ('.' in basename):
            return ''
        return basename.split('.')[-1].strip().lower()

    @staticmethod
    def _generate_s3( # never call this method directly, use TreeStructure.generate() instead
        path  : str,
        result: dict[str, str] = None) -> Dict[str, Dict]:
        """
        Recursively find files in an S3 bucket and its subdirectories.
        Parameters:
            path (str): The S3 bucket path to search in.
            root (str): The root directory for relative paths.
        Returns:
            dict: A dictionary with file paths as keys and relative paths as values.
        """
        if result == None:
            result = {}
        scheme  = "s3://"
        charset = "/"
        if not path.startswith(scheme):
            raise ValueError(f"Path must start with '{scheme}'")
        path = path[len(scheme):].strip(charset)
        if not path:
            raise ValueError("Path cannot be empty")
        bucket_name = path.split("/")[0].strip(charset)
        sub_path    = path[len(bucket_name):].strip(charset)
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")
        s3_client = boto3.client('s3')
        paginator = s3_client.get_paginator('list_objects_v2')
        pages     = paginator.paginate(
            Bucket = bucket_name,
            Prefix = sub_path
        )
        for page in pages:
            if "Contents" not in page:
                continue
            for obj in page['Contents']:
                key = obj['Key']
                if key.endswith('/'):
                    continue
                relative_path = key[len(sub_path):].lstrip(charset)
                full_path     = f"s3://{bucket_name}/{key}"
                response      = s3_client.head_object(Bucket=bucket_name, Key=key)
                filesinfo     = {
                    "name"         : os.path.basename(relative_path),
                    "type"         : "folder" if key.endswith('/') else "file",
                    "depth"        : relative_path.count('/'),
                    "etag"         : response['ETag'],
                    "last_modified": str(response['LastModified']),
                    "content_type" : response.get('ContentType'),
                    "size"         : response['ContentLength'],
                    "children"     : None,
                    "keywords"     : None
                }
                result[full_path] = filesinfo
        return result
	
    @staticmethod
    def generate(
        path               : str,
        base_dir           : str = None,
        result             : dict[str, str] = None,
        extensions         : list[str] = None,
        excluded_extensions: list[str] = None,
        excluded_names     : list[str] = None,
        callback           = None,
        ignore_hidden      : bool = False,
        depth              : int  = 1
        ) -> Dict[str, Dict]:
        """
        Recursively find files in a directory and its subdirectories.
        Parameters:
            dirname (str): The directory to search in.
            base_dir (str): The base directory for relative paths.
            result (dict): A dictionary to store the results.
            extensions (list): List of file extensions to include.
            excluded_extensions (list): List of file extensions to exclude.
            excluded_names (list): List of filenames to exclude.
            callback: A callback function to call for each found file.
            ignore_hidden (bool): Whether to ignore hidden files.
        Returns:
            dict: A dictionary with file paths as keys and relative paths as values.
        """
        path = path.strip()
        if path.startswith("s3://"):
            return (TreeStructure._generate_s3(path = path, result = result))
        if path.startswith("local-data://"):
            path = get_local_data_dir() + path[len("local-data://"):]
        path = os.path.realpath(path).rstrip("/\\")
        if not base_dir:
            base_dir = path
        if result == None:
            result = {}
        try   : files = os.listdir(path)
        except: files = []
        for basename in files:
            if excluded_names and (basename in excluded_names):
                continue
            if ignore_hidden and basename.startswith('.'):
                continue
            if excluded_extensions and (TreeStructure.get_file_extension(basename) in excluded_extensions):
                continue
            if extensions and (TreeStructure.get_file_extension(basename) not in extensions):
                continue
            filename = os.path.realpath(os.path.join(path, basename))
            TreeStructure.generate(
                path                = filename,
                base_dir            = base_dir,
                result              = result,
                extensions          = extensions,
                excluded_extensions = excluded_extensions,
                excluded_names      = excluded_names,
                ignore_hidden       = ignore_hidden,
				depth               = depth + 1
			)
            try    : children = os.listdir(filename)
            except : children = []
            if callback:
                callback(filename)
            result["local-data://" + filename[len(base_dir):].strip("/\\")] = {
            	"depth"       : depth,
            	"name"        : basename,
            	"type"        : "folder" if os.path.isdir(filename) else "file",
            	"content_type": None     if os.path.isdir(filename) else TreeStructure.content_type(filename),
            	"children"    : children if children else None,
                "keywords"    : None
            }
        return (result)

    @staticmethod
    def init_metadata(structure: Dict[str, Dict]) -> Dict[str, Dict]:
        for filename, fileinfo in list(structure.items()):
            try:
                fp     = FileReader(filename, "csv")
                result = fp.read_dataframe()
            except Exception as e:
                logger.info(f"Error reading file {filename}: {e}")
                continue
            metadata = {
                "columns" : {
                    "names" : result.columns.tolist(),
                    "dtypes": {str(k): str(v) for k, v in result.dtypes.to_dict().items()}
                },
                "head": json.loads(result.head(3).to_json(orient='records')),
                "tail": json.loads(result.tail(3).to_json(orient='records'))
            }
            metadata["head_size"] = len(metadata["head"])
            metadata["tail_size"] = len(metadata["tail"])
            structure[filename]["metadata"] = metadata
        return structure

    @staticmethod
    async def update_metadata(structure: Dict[str, Dict]) -> Dict[str, Dict]:
        # return structure # remove me
        for filename, fileinfo in list(structure.items()):
            metadata_response = await get_metadata(
                MetaDataRequest(
                    filepath = filename
                )
            )
            metadata_result = json.loads(metadata_response.body)["result"]
            if metadata_result:
                for key, val in metadata_result.items():
                    fileinfo[key] = val
                ## structure.clear() # remove me
                structure[filename] = fileinfo
                ## break # remove me
        return structure

    @staticmethod
    def tree_description(structure: Dict[str, Dict], depth: int = 0) -> str:
        raise NotImplementedError("This method is not implemented yet.")

    @staticmethod
    def directories(structure: Dict[str, Dict]) -> Dict[str, List[str]]:
        paths = {}
        for path, config in structure.items():
            children = config.get("children")
            if not children:
                continue
            for child in children:
                child_path = path.strip("/") + "/" + child.strip("/")
                paths[child_path] = {}
            paths[path] = {}
        for path in paths.copy():
            scheme = ""
            if "://" in path:
                scheme = path[:path.index("://") + len("://")]
            parent = scheme
            for item in path[len(scheme):].split("/"):
                parent += item
                paths[parent] = {}
                parent += "/"
        for path in paths.copy():
            basename = path.split("/")[-1]
            path     = path[:-len(basename)]
            if path.endswith("://"):
                continue
            paths[path.strip("/")][basename] = 1
        for path, children in paths.items():
            if path in structure:
                continue
            children = list(children.keys())
            structure[path] = {
                "depth"       : -1,
                "name"        : path.strip("/").split("/")[-1],
                "type"        : "folder",
                "content_type": None,
                "children"    : children if children else None,
                "keywords"    : None
            }
        return structure

    @staticmethod
    def graph(structure: Dict[str, Dict]) -> str:
        raise NotImplementedError(
            "This method is not implemented yet. Use TreeStructure.mermaid_graph() instead."
        )
    
    @staticmethod
    def roots(structure: Dict[str, Dict]) -> List[str]:
        """ Get the root directories from the structure.
        Args:
            structure (Dict[str, Dict]): The directory structure.
        Returns:
            List[str]: A list of root directories.
        """
        paths = set()
        for path, config in structure.items():
            if not config.get("children"):
                continue
            shceme = ""
            if "://" in path:
                shceme = path[:path.index("://") + len("://")]
            paths.add( shceme + path[len(shceme):].split("/")[0].strip("/") )
        return sorted(paths)

    @staticmethod
    async def element_description(
        element  : Dict,
        path     : str,
        structure: Dict[str, Dict]) -> str:
        """Generate a description for a single directory element.
        Args:
            element (Dict): The directory element.
        Returns:
            str: A description of the directory element.
        """
        metadata = element.get("metadata", {})
        if not isinstance(metadata, dict) or not metadata:
            raise ValueError("Element metadata is not a valid dictionary or is empty.")
        dbx_client = ChatProxyClient(base="ollama")
        messages = [
            {
                "role"    : "user",
                "content" : [
                    {
                        "text": json.dumps(metadata, indent = 4)
                    }
                ]
            }
        ]
        system_prompt = load_system_prompt("metadata")
        for try_count in range(3):
            response = await dbx_client.send(
                messages      = messages,
                system_prompt = system_prompt,
                model         = "databricks-meta-llama-3-3-70b-instruct",
                temperature   = 0.3,
                max_tokens    = 2000
            )
            if response["error"]:
                logger.error(f"Error in metadata response: {response.get('message', 'Unknown error')}")
                time.sleep(1)
                continue
            try:
                validator = MetadataValidator(
                    text           = response["content"],
                    column_names   = metadata["columns"]["names"],
                    raise_on_error = True
                )
            except Exception as e:
                logger.error(f"Metadata validation failed: {str(e)}")
                continue
            structure[path]["general_description"] = validator.general_description
            structure[path]["column_descriptions"] = validator.column_descriptions
            return structure
        return structure

    @staticmethod
    async def group_description(group: List[Dict]) -> str:
        body = {
            "files"       : [],
            "directories" : []
        }
        for element in group:
            if ("general_description" in element) and ("column_descriptions" in element):
                body["files"].append(
                    {
                        "general_description": element["general_description"],
                        "column_descriptions": element["column_descriptions"]
                    }
                )
            elif ("general_description" in element):
                body["directories"].append(
                    {
                        "general_description": element["general_description"]
                    }
                )
        if not body["files"] and not body["directories"]:
            raise ValueError("Group is empty or does not contain valid elements.")
        client = ChatProxyClient(base="databricks")
        messages = [
            {
                "role"    : "user",
                "content" : [
                    {
                        "text": json.dumps(body, indent = 4)
                    }
                ]
            }
        ]
        system_prompt = load_system_prompt("tree_description")
        for try_count in range(3):
            response = await client.send(
                messages      = messages,
                system_prompt = system_prompt,
                temperature   = 0,
                max_tokens    = 2000
            )
            if response["error"]:
                logger.error(f"Error[group_description]: {response.get('message', 'Unknown error')}")
                time.sleep(1)
                continue
            try:
                validator = DescriptionValidator(
                    text           = response["content"],
                    raise_on_error = True
                )
            except Exception as e:
                logger.error(f"Metadata validation failed: {str(e)}")
                continue
            return validator.general_description
        return None

    @staticmethod
    async def tree_description(structure: Dict[str, Dict]) -> Dict[str, Dict]:
        """Generate a general description for each directory in the structure.
        Algorithm:
            - Name: BFS from bottom to top
            - Description: This algorithm traverses the directory structure in a breadth-first manner,
            - Time Complexity: O(n * depth), where n is the number of directories and depth is the maximum depth of the directory tree.
            - Steps:
                1. Start with the root directories.
                2. For each root, check if it has a general description.
                3. If it does, mark it as visited.
                4. If it doesn't, check its children.
                5. If a parent has enough descripted children, generate a general description for it.
                6. Repeat until all roots are visited.
        Args:
            Structure (Dict[str, Dict]): The directory structure.
        Returns:
            Dict[str, Dict]: The updated structure with general descriptions.
        """
        CHUNK_SIZE    = 5
        roots         = TreeStructure.roots(structure)
        visited_roots = {}
        structure     = TreeStructure.directories(structure)
        while len(visited_roots) < len(roots):
            for path, config in list(structure.items()):
                if (path in roots) and config.get("general_description"):
                    visited_roots[path] = True
                if config.get("general_description"):
                    continue
                if not config.get("children"):
                    await TreeStructure.element_description(config, path, structure)
                    continue
                descripted_children = []
                for child in config["children"]:
                    child_path = path.strip("/") + "/" + child.strip("/")
                    if not structure.get(child_path):
                        continue
                    child_config = structure[child_path]
                    if not child_config.get("general_description"):
                        continue
                    descripted_children.append( child_config )
                if ( len(descripted_children) >= min(CHUNK_SIZE, len(config["children"])) ):
                    structure[path]["general_description"] = await TreeStructure.group_description(descripted_children)
        return structure