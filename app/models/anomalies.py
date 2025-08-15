from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CreateStructureRequest(BaseModel):
    """
        {
            "destination": "",
            "sources": {
                "local-data://Category/Product_Catgories.csv": {
                    "destination": "local-data://my-result.json",
                    "max_depth"  : None
                }
            }
        }
    """
    folder_paths: List[str] = Field(..., description="List of folder paths to analyze")

class MetadataSampleRequest(BaseModel):
    """
        - Exmaple 1:
            {
                "structure": {
                    "local-data://Category/Product_Catgories.csv": {
                       ...
                    }
                },
                "destination": "local-data://my-result.json"
            }
        - Exmaple 2:
            {
                "structure"  : "local-data://path/to/structure.json"
                "destination": "local-data://my-result.json"
            }
    """
    destination: str = Field(..., description="Destination path for the analysis result")
    structure  : str = Field(..., description="Path to the structure file or a dictionary of structure data")