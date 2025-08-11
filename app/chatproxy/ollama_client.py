import os
import sys

import baisstools
baisstools.insert_syspath(__file__, matcher = [r"^baiss_.*$"])

import logging
import time
from typing import List, Dict, Any
from app.chatproxy.base_client import BaseClient

logger = logging.getLogger(__name__)

try:
	import ollama
except ImportError:
	logger.error("Ollama package not found. Install with: pip install ollama")
	ollama = None

class OllamaClient(BaseClient):
	"""
	OllamaClient for interacting with local Ollama models.
	Provides offline AI capabilities using locally hosted models.
	"""
	
	def __init__(self, model_name: str = None, host: str = None):
		"""
		Initialize the LocalClient with a model name and optional host.
		
		Args:
			model_name (str): Name of the Ollama model to use
			host (str): Ollama server host (default: localhost:11434)
		"""
		super().__init__()
		
		self._model_name = model_name
		self._host = host or "http://localhost:11434"
		
		if not ollama:
			raise RuntimeError("Ollama package is required. Install with: pip install ollama")
		
		# Configure Ollama client if host is specified
		if self._host != "http://localhost:11434":
			ollama.Client(host=self._host)
	
	async def send(self, messages: List[Dict[str, Any]], system_prompt: str = None, raise_exception: bool = False, **kwargs) -> Dict[str, Any]:
		"""
		Send messages to the local Ollama model.
		
		Args:
			messages: List of message dictionaries
			system_prompt: Optional system prompt
			raise_exception: Whether to raise exceptions or return error response
			**kwargs: Additional parameters (temperature, top_p, etc.)
		
		Returns:
			Dict with response data in standard format
		"""
		logger.debug(f"Sending messages to local model: {self._model_name}")
		
		# Clean and format messages
		jrequest = self._clean_request(messages, system_prompt)
		formatted_messages = jrequest["messages"]
		system_prompt_text = jrequest["system_prompt"]
		
		if not formatted_messages:
			error_msg = "Messages cannot be empty."
			if raise_exception:
				raise ValueError(error_msg)
			else:
				logger.error(error_msg)
				return {
					"status": 400,
					"success": False,
					"error": error_msg,
					"response": {}
				}
		
		# Convert to Ollama format
		ollama_messages = self._convert_to_ollama_format(formatted_messages, system_prompt_text)
		
		# Extract generation options from kwargs
		options = {
			"temperature": kwargs.get("temperature", 0.7),
			"top_p": kwargs.get("top_p", 0.9),
			"top_k": kwargs.get("top_k", 40),
			"repeat_penalty": kwargs.get("repeat_penalty", 1.1),
			"num_predict": kwargs.get("max_tokens", kwargs.get("max_new_tokens", 30000))
		}
		
		try:
			start_time = time.time()
			
			# Make request to Ollama using instance model name
			response = ollama.chat(
				model=self._model_name,
				messages=ollama_messages,
				stream=False,
				options=options,
				think=False,
				keep_alive=kwargs.get("keep_alive", "30m")  # Changed from True to "30m" to keep models alive longer
			)
			
			inference_time = time.time() - start_time
			logger.debug(f"Local model response time: {inference_time:.2f}s")
			
			return self._decode_ollama_response(response, inference_time)
			
		except Exception as e:
			error_msg = f"Local model request failed: {str(e)}"
			logger.error(error_msg)
			
			if raise_exception:
				raise RuntimeError(error_msg) from e
			
			return {
				"status": 500,
				"success": False,
				"error": error_msg,
				"response": {}
			}
	
	def ping(self, raise_exception: bool = False) -> bool:
		"""
		Check if the local Ollama service and model are available.
		
		Args:
			raise_exception: Whether to raise exceptions on failure
			
		Returns:
			bool: True if service is available, False otherwise
		"""
		try:
			# Test with minimal request
			test_response = ollama.chat(
				model=self._model_name,
				messages=[{"role": "user", "content": "ping"}],
				stream=False,
				options={"num_predict": 1}
			)
			
			# Check if we got a valid response
			success = bool(test_response and test_response.get("message"))
			logger.debug(f"Local model ping {'successful' if success else 'failed'}")
			return success
			
		except Exception as e:
			error_msg = f"Local model ping failed: {str(e)}"
			logger.warning(error_msg)
			
			if raise_exception:
				raise RuntimeError(error_msg) from e
			
			return False
	
	def _encoded_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""
		Encode messages for the local model (no special encoding needed for Ollama).
		
		Args:
			messages: List of message dictionaries
			
		Returns:
			List of encoded messages
		"""
		return messages
	
	def _convert_to_ollama_format(self, messages: List[Dict[str, Any]], system_prompt: str = None) -> List[Dict[str, Any]]:
		"""
		Convert messages to Ollama chat format.
		
		Args:
			messages: Cleaned messages from base client
			system_prompt: Optional system prompt
			
		Returns:
			List of messages in Ollama format
		"""
		ollama_messages = []
		
		# Add system prompt if provided
		if system_prompt and system_prompt.strip():
			ollama_messages.append({
				"role": "system",
				"content": system_prompt.strip()
			})
		
		# Convert messages
		for message in messages:
			role = message.get("role", "user")
			content_parts = message.get("content", [])
			
			# Extract text from content parts
			text_content = ""
			for part in content_parts:
				if isinstance(part, dict) and "text" in part:
					text_content += part["text"] + " "
				elif isinstance(part, str):
					text_content += part + " "
			
			text_content = text_content.strip()
			
			if text_content:
				ollama_messages.append({
					"role": role,
					"content": text_content
				})
		
		return ollama_messages
	
	def _decode_ollama_response(self, response: Dict[str, Any], inference_time: float = 0) -> Dict[str, Any]:
		"""
		Decode Ollama response to standard format matching GeminiClient.
		
		Args:
			response: Raw Ollama response
			inference_time: Time taken for inference
			
		Returns:
			Standardized response dictionary matching GeminiClient format
		"""
		try:
			message = response.get("message", {})
			content = message.get("content", "")
			
			# Calculate tokens (approximate)
			prompt_tokens = response.get("prompt_eval_count", 0)
			completion_tokens = response.get("eval_count", 0)
			total_tokens = prompt_tokens + completion_tokens
			
			# Format response to match GeminiClient structure
			return {
				"status": 200,
				"success": True,
				"error": "",
				"response": {
					"messages": [
						{
							"role": "assistant",
							"content": [{"text": content}]
						}
					]
				},
				"usage": {
					"inputTokens": prompt_tokens,
					"outputTokens": completion_tokens,
					"totalTokens": total_tokens
				},
				"metadata": {
					"inference_time": f"{inference_time*1000:.3f}ms",
					"eval_duration": response.get("eval_duration", 0),
					"load_duration": response.get("load_duration", 0),
					"prompt_eval_duration": response.get("prompt_eval_duration", 0),
					"model": response.get("model", self._model_name)
				}
			}
			
		except Exception as e:
			logger.error(f"Failed to decode Ollama response: {e}")
			return {
				"status": 500,
				"success": False,
				"error": f"Response decoding failed: {str(e)}",
				"response": {}
			}
	
	def list_models(self) -> List[str]:
		"""
		List available local models.
		
		Returns:
			List of model names
		"""
		try:
			models = ollama.list()
			return [model["name"] for model in models.get("models", [])]
		except Exception as e:
			logger.error(f"Failed to list models: {e}")
			return []
	
	def pull_model(self, model_name: str = None) -> bool:
		"""
		Pull/download a model to the local system.
		
		Args:
			model_name: Model to pull (defaults to current model)
			
		Returns:
			bool: Success status
		"""
		target_model = model_name or self._model_name
		
		try:
			logger.info(f"Pulling model: {target_model}")
			ollama.pull(target_model)
			logger.info(f"Successfully pulled model: {target_model}")
			return True
		except Exception as e:
			logger.error(f"Failed to pull model {target_model}: {e}")
			return False
	
	def delete_model(self, model_name: str) -> bool:
		"""
		Delete a local model.
		
		Args:
			model_name: Model to delete
			
		Returns:
			bool: Success status
		"""
		try:
			logger.info(f"Deleting model: {model_name}")
			ollama.delete(model_name)
			logger.info(f"Successfully deleted model: {model_name}")
			return True
		except Exception as e:
			logger.error(f"Failed to delete model {model_name}: {e}")
			return False
	
	def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
		"""
		Get information about a model.
		
		Args:
			model_name: Model to get info for (defaults to current model)
			
		Returns:
			Dictionary with model information
		"""
		target_model = model_name or self._model_name
		
		try:
			info = ollama.show(target_model)
			return {
				"name": info.get("name", target_model),
				"size": info.get("size", 0),
				"digest": info.get("digest", ""),
				"modified": info.get("modified_at", ""),
				"details": info.get("details", {}),
				"modelfile": info.get("modelfile", "")
			}
		except Exception as e:
			logger.error(f"Failed to get model info for {target_model}: {e}")
			return {}
