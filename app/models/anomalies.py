from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CreateStructureRequest(BaseModel):
    """
        {
            "folder_paths": [""]
        }
    """
    folder_paths: List[str] = Field(..., description="List of folder paths to analyze")

class MetadataSampleRequest(BaseModel):
    """
        jsons_paths = ["local-data://path/to/raw1.json", "local-data://path/to/raw2.json"]
    """
    jsons_paths: List[str] = Field(..., description="List of raw JSON file paths")