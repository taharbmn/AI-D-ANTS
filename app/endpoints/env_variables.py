from fastapi import APIRouter, HTTPException, status
from typing import Dict
from app.schemas.env_variables import (
    EnvVariableCreate,
    EnvVariableUpdate,
    EnvVariableResponse,
    EnvVariablesCreate,
    EnvVariablesResponse,
    EnvVariablesList
)
from app.core.env_manager import env_manager

router = APIRouter()

@router.post("/variables", response_model=EnvVariablesResponse)
async def create_env_variables(env_vars: EnvVariablesCreate):
    """
    Crée ou met à jour plusieurs variables d'environnement dans le fichier .env
    """
    success, message = env_manager.set_variables(env_vars.variables)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )

    return EnvVariablesResponse(
        variables=env_vars.variables,
        success=True,
        message=message
    )

@router.post("/variable", response_model=EnvVariableResponse)
async def create_env_variable(env_var: EnvVariableCreate):
    """
    Crée ou met à jour une variable d'environnement dans le fichier .env
    """
    success = env_manager.set_variable(env_var.key, env_var.value)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set environment variable {env_var.key}"
        )

    return EnvVariableResponse(
        key=env_var.key,
        value=env_var.value,
        success=True,
        message=f"Environment variable {env_var.key} set successfully"
    )

@router.get("/variables", response_model=EnvVariablesList)
async def get_all_env_variables():
    """
    Récupère toutes les variables d'environnement du fichier .env
    """
    variables = env_manager.get_all_variables()
    return EnvVariablesList(variables=variables)

@router.get("/variable/{key}")
async def get_env_variable(key: str):
    """
    Récupère une variable d'environnement spécifique
    """
    value = env_manager.get_variable(key)
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environment variable {key} not found"
        )

    return {"key": key, "value": value}

@router.put("/variable/{key}", response_model=EnvVariableResponse)
async def update_env_variable(key: str, env_var: EnvVariableUpdate):
    """
    Met à jour une variable d'environnement existante
    """
    # Vérifier si la variable existe
    existing_value = env_manager.get_variable(key)
    if existing_value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environment variable {key} not found"
        )

    success = env_manager.set_variable(key, env_var.value)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update environment variable {key}"
        )

    return EnvVariableResponse(
        key=key,
        value=env_var.value,
        success=True,
        message=f"Environment variable {key} updated successfully"
    )

@router.delete("/variable/{key}")
async def delete_env_variable(key: str):
    """
    Supprime une variable d'environnement du fichier .env
    """
    success = env_manager.delete_variable(key)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environment variable {key} not found or could not be deleted"
        )

    return {"message": f"Environment variable {key} deleted successfully"}
