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
import boto3
import pandas as pd
from dotenv import load_dotenv
from app.utils import get_local_data_dir

# Load environment variables once at module level
load_dotenv()


try:
    global_s3_client = boto3.client('s3')
except Exception as e:
    raise RuntimeError(f"Failed to create S3 client: {e}")

class FileWriter:
    """Class to write files to S3 or local storage."""
    def __init__(self):
        raise 

class FileReader:
    """Class to read files from S3 or local storage."""
    def __init__(self, file_path: str):
        if str(file_path).strip().lower().startswith("s3://"):
            self._schema    = "s3"
            self._s3_client = global_s3_client
        elif str(file_path).strip().lower().startswith("local-data://"):
            self._schema = "local-data"
        else:
            raise ValueError("Invalid file path. Must start with 's3://' or 'local-data://'.")
        self._file_path = self.clean_file_path(file_path)

        # TODO: Detect file type from mime type or content if possible
        self._file_type = str(file_path).strip().strip(".").split(".")[-1].strip()

        if str(file_path).strip().lower().endswith("/_delta_log"):
            self._file_type = "delta"
            # remove the "_delta_log" suffix from the file path
            self._file_path = self._file_path[:self._file_path.rindex("/_delta_log")].strip()
    
    def clean_file_path(self, file_path: str) -> str:
        """Clean and validate the file path."""
        file_path = str(file_path).strip()
        if (".." in file_path):
            raise ValueError("Invalid Path: File path cannot contain '..'")
        if not file_path:
            raise ValueError("File path cannot be empty.")
        return file_path
    
    def read_dataframe(self):
        """Read a file into a pandas DataFrame based on the file type."""
        if self._file_type == "csv":
            return self.read_csv_dataframe()
        elif self._file_type == "xlsx":
            return self.read_xlsx_dataframe()
        elif self._file_type == "parquet":
            return self.read_parquet_dataframe()
        elif self._file_type == "delta":
            raise ValueError("Delta files are not supported yet.")

        raise ValueError(f"Unsupported file type: {self._file_type}. Supported types are: csv, xlsx, parquet.")

    def read_csv_dataframe(self):
        """Read a CSV file from S3 or local storage."""
        if self._schema == "s3":
            bucket_name = self._file_path.split("://")[1].strip("/").split("/")[0]
            _key        = self._file_path[self._file_path.index("://") + 2:]
            _key        = _key.strip("/")
            _key        = _key[_key.index("/"):].strip("/")
            _s3_obj     = self._s3_client.get_object(Bucket = bucket_name, Key = _key)
            return pd.read_csv(io.BytesIO(_s3_obj['Body'].read()))
        elif self._schema == "local-data":
            subpath = self._file_path[self._file_path.index("://") + 2:].strip("/")
            newpath = os.path.join(get_local_data_dir(), subpath)
            if not os.path.exists(newpath):
                raise FileNotFoundError(f"File not found: {newpath}")
            return pd.read_csv(newpath)
    
    def read_xlsx_dataframe(self):
        """Read an Excel file from S3 or local storage."""
        if self._schema == "s3":
            bucket_name = self._file_path.split("://")[1].strip("/").split("/")[0]
            _key        = self._file_path[self._file_path.index("://") + 2:]
            _key        = _key.strip("/")
            _key        = _key[_key.index("/"):].strip("/")
            _s3_obj     = self._s3_client.get_object(Bucket = bucket_name, Key = _key)
            return pd.read_excel(io.BytesIO(_s3_obj['Body'].read()))
        elif self._schema == "local-data":
            subpath = self._file_path[self._file_path.index("://") + 2:].strip("/")
            newpath = os.path.join(get_local_data_dir(), subpath)
            if not os.path.exists(newpath):
                raise FileNotFoundError(f"File not found: {newpath}")
            return pd.read_excel(newpath)
    
    def read_parquet_dataframe(self):
        """Read a Parquet file from S3 or local storage."""
        if self._schema == "s3":
            bucket_name = self._file_path.split("://")[1].strip("/").split("/")[0]
            _key        = self._file_path[self._file_path.index("://") + 2:]
            _key        = _key.strip("/")
            _key        = _key[_key.index("/"):].strip("/")
            _s3_obj     = self._s3_client.get_object(Bucket = bucket_name, Key = _key)
            return pd.read_parquet(io.BytesIO(_s3_obj['Body'].read()))
        elif self._schema == "local-data":
            subpath = self._file_path[self._file_path.index("://") + 2:].strip("/")
            newpath = os.path.join(get_local_data_dir(), subpath)
            if not os.path.exists(newpath):
                raise FileNotFoundError(f"File not found: {newpath}")
            return pd.read_parquet(newpath)
    
    
    def read_delta_dataframe(self):
        """Read a Delta file from S3 or local storage."""
        from deltalake import DeltaTable
        if self._schema == "s3":
            bucket_name = self._file_path.split("://")[1].strip("/").split("/")[0]
            _key        = self._file_path[self._file_path.index("://") + 2:]
            _key        = _key.strip("/")
            _key        = _key[_key.index("/"):].strip("/")
            _s3_obj     = self._s3_client.get_object(Bucket = bucket_name, Key = _key)
            return DeltaTable(io.BytesIO(_s3_obj['Body'].read())).to_pandas()
        elif self._schema == "local-data":
            subpath = self._file_path[self._file_path.index("://") + 2:].strip("/")
            newpath = os.path.join(get_local_data_dir(), subpath)
            if not os.path.exists(newpath):
                raise FileNotFoundError(f"File not found: {newpath}")
            return DeltaTable(newpath).to_pandas()
    
    @staticmethod
    def readfile(path: str) -> str:
        """Read a file from S3 or local storage and return its content as a string."""
        if str(path).strip().lower().startswith("s3://"):
            bucket_name = path.split("://")[1].strip("/").split("/")[0]
            _key        = path[path.index("://") + 2:]
            _key        = _key.strip("/")
            _key        = _key[_key.index("/"):].strip("/")
            _s3_obj     = global_s3_client.get_object(Bucket = bucket_name, Key = _key)
            return _s3_obj['Body'].read().decode('utf-8')
        elif str(path).strip().lower().startswith("local-data://"):
            subpath = path[path.index("://") + 2:].strip("/")
            newpath = os.path.join(get_local_data_dir(), subpath)
            if not os.path.exists(newpath):
                raise FileNotFoundError(f"File not found: {newpath}")
            with open(newpath, 'r') as file:
                return file.read()
        else:
            raise ValueError("Invalid file path. Must start with 's3://' or 'local-data://'.")