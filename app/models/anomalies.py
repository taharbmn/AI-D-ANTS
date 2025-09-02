from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CreateStructureRequest(BaseModel):
    """
        {
            "folder_paths": [""]
        }
    """
    folder_paths: List[str] = Field(..., description="List of folder paths to analyze")
    model_type: str = Field(..., description="Model type for structure creation")

class MetadataSampleRequest(BaseModel):
    """
        jsons_paths = ["local-data://path/to/raw1.json", "local-data://path/to/raw2.json"]
    """
    jsons_paths: List[str] = Field(..., description="List of raw JSON file paths")
    model_type: str = Field(..., description="Model type for metadata extraction")