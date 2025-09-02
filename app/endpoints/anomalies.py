"""
    Anomalies Endpoints
    This module contains endpoints related to anomalies, including creating structures,
    metadata sampling, and tree descriptions.
    Endpoints:
        1. Create Structure      - POST /anomalies/create-structure
        2. Metadata Sample       - POST /anomalies/create-structure
        3. Metadata Description  - POST /anomalies/create-structure
        4. Tree Description      - POST /anomalies/create-structure
"""

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
import json
import logging
from fastapi                import APIRouter
from typing                 import List, Dict, Optional
from pathlib                import Path
from app.models.anomalies   import CreateStructureRequest, MetadataSampleRequest
from fastapi.responses      import JSONResponse
from app.files.files        import FileReader
from app.files.structures   import TreeStructure

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Also create a console handler to ensure logs show up
formatter       = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create router
router = APIRouter()

@router.post("/create-raw-structure")
async def create_structure(request: CreateStructureRequest):
    """
    Create a structure based on the provided request.
    This endpoint processes the request to create a tree structure
    from the provided paths and their configurations.
        {
            "folder_paths": [
                "s3://bucket_name/path/to",
                "path/to"
            ]
        }
    """

    logger.info(f"Received create structure request")
    local_structures   = []
    list_of_destinations = []
    for path in request.folder_paths:
        path_destination = TreeStructure.get_path_for_raw_tree_structure() + path.replace("://", "_").replace("/", "_") + ".json"
        logger.info(f"Processing path: {path} with destination: {path_destination}")
        if isinstance(path_destination, str) and path_destination.strip():
            path_destination = path_destination.strip()
            path_structure   = {}
            TreeStructure.generate(
                path   = path,
                result = path_structure
            )
            # save local structure permanently
            try:
                TreeStructure.save(
                    structure   = path_structure,
                    destination = path_destination
                )
                list_of_destinations.append(path_destination)
            except Exception as e:
                logger.error(f"Failed to save local structure for {path}: {e}")
            local_structures.append(path_structure)
        else:
            raise ValueError("Invalid path destination")

    # logger.info(f"Paths to local structures: {paths}")
    return JSONResponse(
        status_code = 200,
        content = {
            "response"   : list_of_destinations,
            "success"    : True,
            "status"     : 200
        }
    )

@router.post("/metadata-sample")
async def metadata_sample(request: MetadataSampleRequest):
    raw_jsons_paths = request.jsons_paths
    logger.info(f"Received metadata sample request for paths: {raw_jsons_paths}")
    list_of_destinations = []
    for raw_json_path in raw_jsons_paths:
        file_reader = FileReader(raw_json_path)
        structure   = file_reader.content
        if isinstance(structure, bytes):
            structure = structure.decode('utf-8')
        destination = TreeStructure.get_path_for_processed_tree_structure() + raw_json_path.split("/")[-1]
        if structure.startswith("{") and structure.endswith("}"):
            try:
                structure = json.loads(structure)
                structure = structure["files"]
            except Exception as e:
                logger.error(f"Failed to parse structure JSON: {e}")
        else:
            raise ValueError("Invalid structure format")
        # Initialize metadata for the structure
        structure = TreeStructure.init_metadata(
            structure = structure
        )
        # Save the structure to the destination
        try:
            TreeStructure.save(
                structure   = structure,
                destination = destination
            )
            list_of_destinations.append(destination)
        except Exception as e:
            logger.error(f"Failed to save structure: {e}")
    return JSONResponse(
        status_code = 200,
        content = {
            "response"   : list_of_destinations,
            "success"    : True,
            "status"     : 200
        }
    )

@router.post("/metadata-description")
async def metadata_description(request: MetadataSampleRequest):
    processed_jsons = request.jsons_paths
    list_of_destinations = []
    for processed_json in processed_jsons:
        file_reader = FileReader(processed_json)
        structure   = file_reader.content
        destination = TreeStructure.get_path_for_processed_tree_structure() + processed_json.split("/")[-1]
        if isinstance(structure, bytes):
            structure = structure.decode('utf-8')
        if structure.startswith("{") and structure.endswith("}"):
            try:
                structure = json.loads(structure)
            except Exception as e:
                logger.error(f"Failed to parse structure JSON: {e}")
        else:
            try:
                structure = json.loads(FileReader.readfile(structure))
            except Exception as e:
                logger.error(f"Failed to read structure from file: {e}")
        # Initialize metadata for the structure
        structure = await TreeStructure.update_metadata(
            structure = structure,
            model_type=request.model_type
        )
        # Save the structure to the destination
        try:
            TreeStructure.save(
                structure   = structure,
                destination = destination
            )
            list_of_destinations.append(destination)
        except Exception as e:
            logger.error(f"Failed to save structure: {e}")
    return JSONResponse(
        status_code = 200,
        content = {
            "response"   : structure,
            "success"    : True,
            "status"     : 200
        }
    )

@router.post("/create_tree_structure")
async def create_tree_structure(request: CreateStructureRequest):
    folder_paths = request.folder_paths
    logger.info(f"Creating tree structure for paths: {folder_paths}")
    try:
        json_folder_path = CreateStructureRequest(
            folder_paths = folder_paths,
            model_type = request.model_type
        )
        raw_tree_structure_response = await create_structure(json_folder_path)
        # raw_paths = raw_tree_structure.get("response", [])
        # Extract the actual content from the JSONResponse
        if hasattr(raw_tree_structure_response, 'body'):
            # For JSONResponse, get the body content
            raw_tree_structure_content = json.loads(raw_tree_structure_response.body.decode('utf-8'))
        else:
            # If it's already a dict, use it directly
            raw_tree_structure_content = raw_tree_structure_response
            
        raw_paths = raw_tree_structure_content.get("response", [])
        logger.info(f"Raw tree structure created for paths: {raw_paths}")

        metadata_sample_request = MetadataSampleRequest(
            jsons_paths = raw_paths,
            model_type  = request.model_type
        )

        try:
            # Process the metadata sample request as needed
            metadata_description_response = await metadata_sample(metadata_sample_request)
        except Exception as e:
            logger.error(f"Failed to process metadata sample request: {e}")
            return JSONResponse(
                status_code = 500,
                content = {
                    "response"   : e,
                    "success"    : False,
                    "status"     : 500
                }
            )
        if hasattr(metadata_description_response, 'body'):
            # For JSONResponse, get the body content
            metadata_description_content = json.loads(metadata_description_response.body.decode('utf-8'))

        processed_paths = metadata_description_content.get("response", [])

        metadata_description_request = MetadataSampleRequest(
            jsons_paths = processed_paths,
            model_type  = request.model_type
        )
        try:
            metadata_description_response = await metadata_description(metadata_description_request)
        except Exception as e:
            logger.error(f"Failed to process metadata description request: {e}")
            return JSONResponse(
                status_code = 500,
                content = {
                    "response"   : e,
                    "success"    : False,
                    "status"     : 500
                }
            )

        if hasattr(metadata_description_response, 'body'):
            # For JSONResponse, get the body content
            metadata_description_content = json.loads(metadata_description_response.body.decode('utf-8'))

        structure = metadata_description_content.get("response", [])

    except Exception as e:
        logger.error(f"Failed to create tree structure: {e}")
        return JSONResponse(
            status_code = 500,
            content = {
                "response"   : "Failed to create tree structure",
                "success"    : False,
                "status"     : 500
            }
        )

    all_structures = TreeStructure.read_all_json_structure(step="processed")

    return JSONResponse(
        status_code = 200,
        content = {
            "response"   : all_structures,
            "success"    : True,
            "status"     : 200
        }
    )

@router.get("/processed_tree_structure")
async def get_processed_tree_structure():
    try:
        processed_tree_structure = TreeStructure.read_all_json_structure(step="processed")
        return JSONResponse(
            status_code=200,
            content={
                "response": processed_tree_structure,
                "success": True,
                "status": 200
            }
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "response": "Processed tree structure not found",
                "success": False,
                "status": 404
            }
        )
    except Exception as e:
        logger.error(f"Failed to get processed tree structure: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "response": "Failed to get processed tree structure",
                "success": False,
                "status": 500
            }
        )