from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from app.models.chat import (
    MetaDataRequest
)
from app.chatproxy.dbx_model import DatabricksModel
from dotenv import load_dotenv
import logging
import json
import time
import uuid
import os
from pathlib import Path
from app.validators.metadata import MetadataValidator
from app.files.files import FileReader
router = APIRouter()
logger = logging.getLogger(__name__)

load_dotenv()

DATA_EXPERT_DURATION = int(os.environ.get("DATA_EXPERT_DURATION", "60"), 10)
 
os.environ["NUMBER_OF_PYTHON_SCRIPTS"] = "5"


def get_metadata_system_prompt() -> str:
    """Read the metadata system prompt from the metadata.md file"""
    try:
        # Get the path to the metadata.md file
        current_dir = Path(__file__).parent.parent
        metadata_file = current_dir / "system_prompt" / "metadata.md"
        
        if not metadata_file.exists():
            logger.warning(f"Metadata system prompt file not found at {metadata_file}")
            return "You are a data analyst. Analyze the provided dataset metadata and provide insights."
        
        with open(metadata_file, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading metadata system prompt: {str(e)}")
        return "You are a data analyst. Analyze the provided dataset metadata and provide insights."


@router.post("/metadata")
async def get_metadata(
    request: MetaDataRequest
):
    """
        Get metadata for a file using AI for analysis
    Args:
        request (MetaDataRequest): The request containing the file path.
    Returns:
        JSONResponse: A response containing the metadata or an error message.
    Example Body:
        {
            "filepath": "s3://test-coder/sales_data_s3.csv"
        }
    """

    
    # Directly call the metadata function instead of HTTP request
    file_metadata_result = get_file_metadata_from_s3(request.filepath, "csv")
    
    if not file_metadata_result["status"]:
        return JSONResponse(
            status_code = 400,
            content = {
                "status" : 400,
                "success": False,
                "result" : None,
                "error"  : file_metadata_result["error"],
            }
        )
    
    # Get system prompt from metadata.md file
    system_prompt = get_metadata_system_prompt()
    
    # Prepare messages for AI
    messages = [
        {
            "role"    : "user",
            "content" : [
                {
                    "text": json.dumps({
                        "columns": {
                            "names" : file_metadata_result["metadata"]["columns"]["names"],
                            "dtypes": file_metadata_result["metadata"]["columns"]["dtypes"]
                        },
                        "head"     : file_metadata_result["metadata"]["sample_data"]["head"],
                        "tail"     : file_metadata_result["metadata"]["sample_data"]["tail"],
                        "head_size": len(file_metadata_result["metadata"]["sample_data"]["head"]),
                        "tail_size": len(file_metadata_result["metadata"]["sample_data"]["tail"])
                    }, indent = 4)
                }
            ]
        }
    ]

    # Initialize Databricks AI client
    dbx_client = DatabricksModel()
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
                column_names   = file_metadata_result["metadata"]["columns"]["names"],
                raise_on_error = True
            )
        except Exception as e:
            logger.error(f"Metadata validation failed: {str(e)}")
            continue
        return JSONResponse(
            status_code = 200,
            content = {
                "status" : 200,
                "success": True,
                "result" : {
                    "metadata"          : file_metadata_result["metadata"],
                    "description"       : validator.general_description,
                    "columnsDescription": validator.column_descriptions
                },
                "error": None
            }
        )
    return JSONResponse(
        status_code = 500,
        content = {
            "status" : 500,
            "success": False,
            "result" : None,
            "error"  : "Failed to process metadata after multiple attempts"
        }
    )


def get_file_data_wrapper(file_path: str) -> Dict[str, Any]:
    """
    Wrapper function to read file data using FileReader and return standardized result.
    
    Args:
        file_path: Path to the file (S3 or local)
        
    Returns:
        Dict with status, result (DataFrame), and error
    """
    try:
        file_reader = FileReader(file_path)
        df = file_reader.read_dataframe()
        return {
            "status": True,
            "result": df,
            "error": None
        }
    except Exception as e:
        return {
            "status": False,
            "result": None,
            "error": str(e)
        }


def get_file_metadata_from_s3(s3_path: str) -> Dict[str, Any]:
    """
    Get metadata of file from S3 using AWS Data Wrangler.
    
    Args:
        s3_path: S3 path to the file (e.g., 's3://bucket/path/file.csv')
        
    Returns:
        Dict with status, result (metadata), error, and execution_time
    """

    start_time = time.perf_counter()


    fileinfo = get_file_data_wrapper(s3_path)
    file_type = s3_path.split('.')[-1].lower() if '.' in s3_path else 'unknown'

    try:
        if (not fileinfo["status"]) or fileinfo["error"]:
            raise ValueError(fileinfo["error"])
        df = fileinfo["result"]
        metadata = {
            "file_info": {
                "path": s3_path,
                "file_type": file_type,
                "shape": {
                    "rows"   : int(df.shape[0]),
                    "columns": int(df.shape[1])
                }
            },
            "columns": {
                "names" : df.columns.tolist(),
                "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
            },
            "sample_data": {
                "head": json.loads(df.head(3).to_json(orient='records')),
                "tail": json.loads(df.tail(3).to_json(orient='records'))
            }
        }
        return {
            "status"   : True,
            "metadata" : metadata,
            "error"    : None,
            "execution_time": f"{(time.perf_counter() - start_time) * 1000:.3f}ms"
        }
    except Exception as e:
        return {
            "status"  : False,
            "metadata": None,
            "error"   : f"Failed to get metadata for {s3_path}. Error: {type(e).__name__}: {str(e)}",
            "execution_time": f"{(time.perf_counter() - start_time) * 1000:.3f}ms"
        }
