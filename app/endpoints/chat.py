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
from typing import List, Dict, Any, Optional
import re
import time
import json
import logging
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import time

from app.files.structures import TreeStructure
from app.models.chat import ChatRequest, DataRequest
from app.models.anomalies import CreateStructureRequest
from app.core.config import system_prompts, client_cache
from app.endpoints.metadata import get_file_metadata
from app.endpoints.anomalies import create_tree_structure
from app.sandbox.execute_code import execute_python_code

from app.extractors.json_extractor import JsonExtractor
from app.extractors.xml_extractor import XmlExtractor

logger = logging.getLogger(__name__)
router = APIRouter()
import uuid
load_dotenv()

@router.post("/brain")
async def chat_endpoint(request: ChatRequest):
    

    try: 
        logging.info("new message")

        

        available_datasets = []
        mapping_id_path = {}
        metadata_details = {}

        if request.available_datasets and len(request.available_datasets) > 0:
            try:
                processed_tree_structure = TreeStructure.read_all_json_structure(step="processed")
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail="Processed tree structure not found. Please ensure the structure is generated before using this endpoint.")

            for path in request.available_datasets:
                if path in processed_tree_structure:
                    dataset_info = processed_tree_structure[path]
                else:
                    # TODO: Enhance this part better to be able to handle when files have been updated as well
                    request_input = CreateStructureRequest(
                        folder_paths=[path]
                    )
                    create_structure = await create_tree_structure(request_input)
                    create_structure_json = json.loads(create_structure.body.decode('utf-8'))
                    dataset_info = create_structure_json["response"][path]
                metadata = dataset_info.get("metadata")
                columns = dataset_info.get("columnsDescription", [])
                description = dataset_info.get("description", "")
                name = dataset_info.get("name", "")
                id = str(uuid.uuid4())
                available_datasets.append({
                    "id": id,
                    "name": name,
                    "description": description,
                    "columns": columns,
                    
                })
                mapping_id_path[id] = path
                metadata_details[id] = metadata


        else:
            available_datasets.append({"empty": True, "message": "No available datasets found."})


        brain_system_prompts = system_prompts.get("brain")

        brain_system_prompts = brain_system_prompts.replace("${variables.brain.settings.available_datasets}", json.dumps(available_datasets))
        brain_system_prompts = brain_system_prompts.replace("${variables.data_expert.settings.current_date}", time.strftime("%Y-%m-%d"))
        # logging.info(f"Brain system prompts: {brain_system_prompts}")
        messages = []

        # Add historical messages if they exist
        if request.messages_historical:
            for msg in request.messages_historical:
                messages.append({
                    "role": msg.role,
                    "content": [{"text": msg.content}]
                })

        # Add the current message
        messages.append({
            "role": request.message.role,
            "content": [{"text": request.message.content}]
        })
        client = client_cache.get("ollama")

        max_conversation_turns = 3
        current_turn = 0
        codes = []
        sources = []

        while current_turn < max_conversation_turns:
            current_turn += 1

            try:
                response = await client.send(
                    messages=messages,
                    system_prompt=brain_system_prompts,
                    temperature=0.1,
                    max_tokens=5000
                )

                ai_messages = response["response"].get("messages")
                last_ai_message = ai_messages[-1]["content"][0]["text"]

                if not last_ai_message:
                    raise HTTPException(status_code=500, detail="No messages in AI response")
                
                messages.append(ai_messages[-1])

                extract_agents = JsonExtractor.extract_objects(last_ai_message)

                logging.info(f"Extracted agents: {json.dumps(extract_agents, indent=2)}")

                if len(extract_agents) > 0:
                    for agent in extract_agents:
                        id = agent.get("id")
                        if not id:
                            raise HTTPException(status_code=400, detail="Agent must include 'id' field")
                        path = mapping_id_path[id]
                        metadata = metadata_details[id]
                        if not path:
                            raise HTTPException(status_code=400, detail=f"Path for agent with id {id} not found")
                        question = agent.get("question")
                        if not question:
                            raise HTTPException(status_code=400, detail="Agent must include 'question' field")
                        data_request = DataRequest(
                            data_source_file=path,
                            message={
                                "role": "user",
                                "content": str(question)
                            },
                            metadata=metadata
                        )
                        sources.append(path)

                        data_response = await create_conversation_with_data_expert(data_request)
                        logging.info(f"Data response for agent {id}: {data_response}")

                        if not data_response:
                            raise HTTPException(status_code=500, detail="No response from data expert")

                        data_response_json = json.loads(data_response.body.decode('utf-8'))

                        if data_response_json.get("success"):
                            code = data_response_json["code"]
                            data_ai_messages = data_response_json["response"].get("messages")
                            data_response_text = data_ai_messages[-1]["content"][0]["text"]
                            message_to_brain = XmlExtractor.create_agent_answer_block(data_response_text)
                            codes.append(code)
                        else:
                            message_to_brain = XmlExtractor.create_agent_answer_block("The request have failed, DO NOT TRY AGAIN, REPORT TO THE USER THAT THERE WAS A PROBLEM IN PROCESSING THE FILE")
                        messages.append({
                            "role": "user",
                            "content": [{"text": message_to_brain}]
                        })
                else:
                    logging.info(f"all messages : {json.dumps(messages, indent=2)}")
                    last_ai_message_extracted = XmlExtractor.extract_answer(last_ai_message)
                    if last_ai_message_extracted:
                        last_ai_message = last_ai_message_extracted
                    return {
                        "status": 200,
                        "success": True,
                        "response": {"messages": [last_ai_message]},
                        "codes": codes,
                        "sources": sources,
                        "error": "",
                        "stop_reason": "end_turn"
                        }
            except Exception as e:
                logger.error(f"Error processing chat request: {str(e)}")
                return {
                    "status": 500,
                    "success": False,
                    "response": {},
                    "codes": codes,
                    "sources": sources,
                    "error": str(e),
                    "stop_reason": "error"
                }
        last_ai_message_extracted = XmlExtractor.extract_answer(last_ai_message)
        if last_ai_message_extracted:
            last_ai_message = last_ai_message_extracted

        return {
            "status": 200,
            "success": True,
            "response": {"messages": [last_ai_message]},
            "codes": codes,
            "sources": sources,
            "error": "",
            "stop_reason": "end_turn"
            }

    except Exception as e:
        logging.error(f"Error processing chat request: {str(e)}")
        return {
            "status": 500,
            "success": False,
            "response": {},
            "codes": "",
            "sources": "",
            "error": str(e),
            "stop_reason": "error"
        }



def extract_python_code(ai_response: str) -> str:
    """Extract Python code from AI response"""
    # Look for code blocks
    code_pattern = r'```python\n(.*?)```'
    matches = re.findall(code_pattern, ai_response, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # If no code blocks found, return the entire response as it might be raw code
    return ai_response.strip()



@router.post("/data_expert")
async def create_conversation_with_data_expert(request: DataRequest):
    """
    Generate and execute Python code to analyze data using AI.
    
    Args:
        request (DataRequest): Contains data_source_file (S3 path) and user message
        
    Returns:
        JSONResponse: Analysis results from executed Python code
    """
    start_time = time.time()
    
    # Validate data source file
    data_source_file = str(request.data_source_file).strip()
    if not data_source_file:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "success": False,
                "response": {},
                "error": "Data source file is required",
                "usage": {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0},
                "stop_reason": "error"
            }
        )
    
    if request.metadata is None or not isinstance(request.metadata, dict):
        logging.warning("No schema information provided in request metadata. Using default schema.")
        try:
            schema_info = get_file_metadata(data_source_file)
        except Exception as e:
            logging.error(f"Error getting metadata for file {data_source_file}: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "success": False,
                    "response": {},
                    "error": f"Failed to get file metadata: {str(e)}",
                    "usage": {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0},
                    "stop_reason": "error"
                }
            )
    else:
        schema_info = request.metadata
    try:

        
        # log the schema info full
        logger.info(f"Schema info: {json.dumps(schema_info, indent=2)}")

        # Get the system prompt with variables substituted
        system_prompt = system_prompts.get("data_expert")
        if not system_prompt:
            raise ValueError("Data engineering system prompt not found in configuration")

        system_prompt = system_prompt.replace("${os.environ[\"NUMBER_OF_PYTHON_SCRIPTS\"]}", "1")
        system_prompt = system_prompt.replace("${variables.data_expert.settings.input_schema}", str(schema_info))
        system_prompt = system_prompt.replace("${variables.data_expert.settings.default_data_source_file}", data_source_file)
        
        # Prepare messages for AI
        user_content = request.message.content
        if isinstance(user_content, list):
            # If content is already a list, use it as is
            content_list = user_content
        else:
            # If content is a string, wrap it in the expected format
            content_list = [{"text": user_content}]
        
        messages = [
            {
                "role": request.message.role,
                "content": content_list
            }
        ]
        
        
        client = client_cache.get("ollama")
        
        # Set timeout and retry configuration
        DATA_EXPERT_DURATION = int(os.environ.get("DATA_EXPERT_DURATION", "60"))
        max_fails_count = 2
        fails_count = 0
        stop_time = time.time() + DATA_EXPERT_DURATION
        
        while (time.time() < stop_time) and (fails_count < max_fails_count):
            try:
                logger.info(f"=== AI REQUEST ATTEMPT {fails_count + 1} ===")
                
                # Get AI response
                response = await client.send(
                    messages=messages,
                    system_prompt=system_prompt,
                    temperature=0.1,
                    max_tokens=5000
                )
                
                print(f"=== AI RESPONSE ===\n{json.dumps(response, indent=2)}")
                
                if response["error"]:
                    fails_count += 1
                    logger.error(f"Error in AI response: {response.get('message', 'Unknown error')}")
                    time.sleep(1)
                    continue
                
                print("-------------------------------------")
                
                # Extract Python code from AI response
                ai_messages = response["response"].get("messages")
                ai_text = ai_messages[-1]["content"][0]["text"]
                logger.info(f"=== AI GENERATED TEXT ===")
                logger.info(f"Raw AI response content:\n{ai_text}")
                print(f"=== AI GENERATED TEXT ===\n{ai_text}")
                
                python_code = extract_python_code(ai_text)
                logging.info(f"=== EXTRACTED PYTHON CODE ===")
                logging.info(f"Extracted code:\n{python_code}")
                print(f"=== EXTRACTED PYTHON CODE ===\n{python_code}")
                
                if not python_code:
                    fails_count += 1
                    logger.error("No Python code found in AI response")
                    continue
                
                logger.info(f"=== EXECUTING PYTHON CODE ===")
                
                # Execute the generated Python code
                execution_result = execute_python_code(
                    code=python_code,
                    datasourcefile=data_source_file
                )
                
                logger.info(f"=== CODE EXECUTION RESULT ===")
                logger.info(f"Execution success: {execution_result['success']}")
                logger.info(f"Execution time: {execution_result.get('execution_time', 'unknown')}")
                if execution_result["success"]:
                    logger.info(f"Execution stdout:\n{execution_result['stdout']}")
                else:
                    logger.error(f"Execution error: {execution_result.get('error', 'Unknown error')}")
                    if execution_result.get('stderr'):
                        logger.error(f"Execution stderr: {execution_result['stderr']}")
                
                if execution_result["success"]:
                    logger.info("=== SUCCESSFUL RESPONSE ===")
                    return JSONResponse(
                        status_code=200,
                        content={
                            "status": 200,
                            "success": True,
                            "response": {
                                "messages": [{
                                    "role": "assistant",
                                    "content": [
                                        {
                                            "text": str(execution_result["stdout"])
                                        }
                                    ]
                                }]
                            },
                            "code": str(python_code),
                            "error": "",
                            "stop_reason": "end_turn",
                            "execution_time": execution_result.get("execution_time", "unknown")
                        }
                    )
                else:
                    fails_count += 1
                    logger.error(f"Code execution failed: {execution_result.get('error', 'Unknown error')}")
                    continue
                    
            except Exception as e:
                fails_count += 1
                logger.error(f"Error in data expert processing: {str(e)}")
                continue
        
        # If we reach here, all attempts failed
        if time.time() >= stop_time:
            error_msg = f"Timeout after {DATA_EXPERT_DURATION} seconds"
        else:
            error_msg = f"Failed to process request after {max_fails_count} attempts"
        
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "response": {},
                "code": "",
                "error": error_msg,
                "usage": {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0},
                "stop_reason": "error"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in data_expert conversation: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "response": {},
                "code": "",
                "error": str(e),
                "usage": {"inputTokens": 0, "outputTokens": 0, "totalTokens": 0},
                "stop_reason": "error"
            }
        )
    


# @router.post("/analyze")
# async def analyze(request: AnalyzeRequest):
#     global_structure   = {}
#     global_destination = request.destination
#     local_structures   = []
#     for path, path_config in request.sources.items():
#         path_destination = path_config.get("destination")
#         if isinstance(path_destination, str) and path_destination.strip():
#             path_destination = path_destination.strip()
#             path_structure   = {}
#             TreeStructure.generate(
#                 path   = path,
#                 result = path_structure
#             )
#             # init metadata for local structure
#             TreeStructure.init_metadata(
#                 structure = path_structure
#             )
#             # update metadata for local structure (using AI, meatadata endpoint)
#             path_structure = await TreeStructure.update_metadata(
#                 structure = path_structure
#             )
#             # save local structure permanently
#             TreeStructure.save(
#                 structure   = path_structure,
#                 destination = path_destination
#             )
#             local_structures.append(path_structure)
#         else:
#             TreeStructure.generate(
#                 path   = path,
#                 result = global_structure
#             )
#     # init metadata for global structure
#     TreeStructure.init_metadata(
#         global_structure
#     )
#     # update metadata for global structure (using AI, metadata endpoint)
#     global_structure = await TreeStructure.update_metadata(
#         structure = global_structure
#     )
#     # save global structure permanently
#     TreeStructure.save(
#         structure   = global_structure,
#         destination = global_destination
#     )
#     # just for API:
#     for local_structure in local_structures:
#         for key, val in local_structure:
#             global_structure[key] = val
#     return JSONResponse(
#         status_code = 200,
#         content = {
#             "response"   : global_structure,
#             "success"    : True,
#             "status"     : 200
#         }
#     )