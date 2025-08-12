from pydantic import BaseModel
from typing import Dict, Any, Optional

class EnvVariableCreate(BaseModel):
    key: str
    value: str

class EnvVariableUpdate(BaseModel):
    value: str

class EnvVariableResponse(BaseModel):
    key: str
    value: str
    success: bool
    message: str

class EnvVariablesCreate(BaseModel):
    variables: Dict[str, str]

class EnvVariablesResponse(BaseModel):
    variables: Dict[str, str]
    success: bool
    message: str

class EnvVariablesList(BaseModel):
    variables: Dict[str, str]
