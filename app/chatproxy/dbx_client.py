import os
import sys
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
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

from .base_client import BaseClient

logger = logging.getLogger(__name__)

class DatabricksModel(BaseClient):
	"""
	Databricks AI Model client using OpenAI API format.
	Extends BaseClient to provide Databricks-specific functionality.
	"""

	def __init__(self, 
				 model_name: str = "databricks-meta-llama-3-3-70b-instruct",
				 base_url: str = None,
				 token: str = None):
		super().__init__()
		self.model_name = model_name
		
		# Get Databricks token from environment
		if not token:
			raise ValueError("Databricks token must be provided")
		self.databricks_token = token

		if not base_url:
			raise ValueError("Databricks base URL must be provided")
		self.base_url = base_url
		
		self.client = OpenAI(
			api_key=self.databricks_token,
			base_url=self.base_url
		)
		
		logger.info(f"Initialized DatabricksModel with model: {self.model_name}")

	async def send(self, messages: List[Dict[str, Any]], system_prompt: str = None, raise_exception: bool = False, **kwargs) -> Dict[str, Any]:
		"""
		Send messages to Databricks AI model via OpenAI API.
		
		Args:
			messages: List of message dictionaries with 'role' and 'content'
			system_prompt: Optional system prompt to prepend
			raise_exception: Whether to raise exceptions or return error dict
			**kwargs: Additional parameters for the API call
			
		Returns:
			Dict containing the response or error information
		"""
		try:
			# Clean and prepare the request
			cleaned_request = self._clean_request(messages, system_prompt)
			
			# Convert to OpenAI format
			openai_messages = self._convert_to_openai_format(
				cleaned_request["messages"], 
				cleaned_request["system_prompt"]
			)
			
			# Prepare API parameters
			api_params = {
				"model": self.model_name,
				"messages": openai_messages,
				**kwargs  # Allow additional parameters like temperature, max_tokens, etc.
			}
			
			# Make the API call
			response = self.client.chat.completions.create(**api_params)


			# to debug answer
			# logger.info(f"DatabricksModel.send response: {response}")
			
			# Decode and return the response
			return self._decode_jresponse(response, raise_exception)
			
		except Exception as e:
			logger.error(f"Error in DatabricksModel.send: {str(e)}")
			if raise_exception:
				raise
			return {
				"error": True,
				"message": str(e),
				"type": "databricks_api_error"
			}

	def ping(self, raise_exception: bool = False) -> bool:
		"""
		Ping the Databricks API to check if it's reachable.
		
		Args:
			raise_exception: Whether to raise exceptions or return False
			
		Returns:
			True if API is reachable, False otherwise
		"""
		try:
			# Send a simple test message
			test_response = self.client.chat.completions.create(
				model=self.model_name,
				messages=[{"role": "user", "content": "ping"}],
				max_tokens=1
			)
			
			logger.info("Databricks API ping successful")
			return True
			
		except Exception as e:
			logger.error(f"Databricks API ping failed: {str(e)}")
			if raise_exception:
				raise
			return False

	def _encoded_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""
		Encode messages to ensure they conform to the expected format.
		For Databricks, we'll keep the same format as the base implementation.
		"""
		return messages

	def _convert_to_openai_format(self, messages: List[Dict[str, Any]], system_prompt: str = "") -> List[Dict[str, str]]:
		"""
		Convert internal message format to OpenAI API format.
		
		Args:
			messages: List of internal format messages
			system_prompt: Optional system prompt
			
		Returns:
			List of messages in OpenAI format
		"""
		openai_messages = []
		
		# Add system prompt if provided - handle None values
		if system_prompt and isinstance(system_prompt, str) and system_prompt.strip():
			openai_messages.append({
				"role": "system",
				"content": system_prompt.strip()
			})
		
		# Convert each message
		for message in messages:
			role = message.get('role', 'user')
			content = message.get('content', [])
			
			# Extract text from content parts
			text_parts = []
			for part in content:
				if isinstance(part, dict) and 'text' in part and part['text'] is not None:
					text_parts.append(str(part['text']))
				elif isinstance(part, str) and part is not None:
					text_parts.append(part)
			
			# Combine text parts - handle None values
			combined_text = ' '.join(text_parts).strip() if text_parts else ""
			
			if combined_text:
				openai_messages.append({
					"role": role,
					"content": combined_text
				})
		
		return openai_messages

	def _decode_jresponse(self, response: Any, raise_exception: bool = False) -> Dict[str, Any]:
		"""
		Decode the response from Databricks API.
		
		Args:
			response: OpenAI response object
			raise_exception: Whether to raise exceptions
			
		Returns:
			Decoded response dictionary
		"""
		try:
			# Extract content from OpenAI response
			if hasattr(response, 'choices') and response.choices:
				choice = response.choices[0]
				content = choice.message.content if hasattr(choice.message, 'content') else ""

				prompt_tokens = getattr(response.usage, 'prompt_tokens', 0) if hasattr(response, 'usage') else 0
				completion_tokens = getattr(response.usage, 'completion_tokens', 0) if hasattr(response, 'usage') else 0
				total_tokens = getattr(response.usage, 'total_tokens', 0) if hasattr(response, 'usage') else 0

				# Build response in internal format
				decoded_response = {
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
                "metadata": {}
            }
				
				return decoded_response
			else:
				error_msg = "No choices in response"
				logger.error(error_msg)
				if raise_exception:
					raise ValueError(error_msg)
				return {
					"error": True,
					"message": error_msg,
					"type": "invalid_response"
				}
				
		except Exception as e:
			logger.error(f"Error decoding Databricks response: {str(e)}")
			if raise_exception:
				raise
			return {
				"error": True,
				"message": str(e),
				"type": "decode_error"
			}

	def get_model_info(self) -> Dict[str, Any]:
		"""
		Get information about the current model configuration.
		
		Returns:
			Dictionary with model information
		"""
		return {
			"model_name": self.model_name,
			"base_url": self.base_url,
			"provider": "databricks",
			"api_format": "openai_compatible"
		}
