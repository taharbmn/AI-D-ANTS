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

@router.post("/create-structure")
async def create_structure(request: CreateStructureRequest):
    """
    Create a structure based on the provided request.
    This endpoint processes the request to create a tree structure
    from the provided paths and their configurations.
        {
            "destination": "s3://path/to/file.json", # or "local-data://" this is the path where the structure will be saved
            "sources": {
                "s3://bucket_name/path/to": {

                }
            }
        }
    """
    global_structure   = {}
    global_destination = request.destination
    local_structures   = []
    for path, path_config in request.sources.items():
        path_destination = path_config.get("destination")
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
            except Exception as e:
                logger.error(f"Failed to save local structure for {path}: {e}")
            local_structures.append(path_structure)
        else:
            TreeStructure.generate(
                path   = path,
                result = global_structure
            )
    # save global structure permanently
    try:
        TreeStructure.save(
            structure   = global_structure,
            destination = global_destination
        )
    except Exception as e:
        logger.error(f"Failed to save global structure: {e}")
    # just for API:
    for local_structure in local_structures:
        for key, val in local_structure:
            global_structure[key] = val
    return JSONResponse(
        status_code = 200,
        content = {
            "response"   : global_structure,
            "success"    : True,
            "status"     : 200
        }
    )

@router.post("/metadata-sample")
async def metadata_sample(request: MetadataSampleRequest):
    destination = request.destination
    structure   = request.structure.strip()
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
    structure = TreeStructure.init_metadata(
        structure = structure
    )
    # Save the structure to the destination
    try:
        TreeStructure.save(
            structure   = structure,
            destination = destination
        )
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

@router.post("/metadata-description")
async def metadata_description(request: MetadataSampleRequest):
    destination = request.destination
    structure   = request.structure.strip()
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
        structure = structure
    )
    # Save the structure to the destination
    try:
        TreeStructure.save(
            structure   = structure,
            destination = destination
        )
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

@router.post("/tree-description")
async def tree_description(request: MetadataSampleRequest):
    destination = request.destination
    structure   = request.structure.strip()
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
    structure = await TreeStructure.tree_description(
        structure = structure
    )
    # Save the structure to the destination
    try:
        TreeStructure.save(
            structure   = structure,
            destination = destination
        )
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