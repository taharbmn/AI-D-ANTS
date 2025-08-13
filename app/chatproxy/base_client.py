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


import logging
from dotenv import load_dotenv
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
load_dotenv()

class BaseClient:
	"""
	BaseClient is a base class for API clients.
	It should be extended by specific API clients like GeminiClient.
	"""

	def __init__(self):
		pass

	async def send(self, messages: List[Dict[str, Any]], system_prompt: str = None, raise_exception: bool = False, **kwargs) -> Dict[str, Any]:
		"""
		Send messages to the API.
		This method should be overridden by subclasses if needed.
		"""
		raise NotImplementedError("This method should be overridden by subclasses.")
	
	def ping(self, raise_exception: bool = False) -> bool:
		"""
		Ping the API to check if it's reachable.
		This method should be overridden by subclasses if needed.
		"""
		raise NotImplementedError("This method should be overridden by subclasses.")

	def _encoded_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		"""
		Encode messages to ensure they conform to the expected format.
		This method should be overridden by subclasses if needed.
		"""
		raise NotImplementedError("This method should be overridden by subclasses.")
	
	def _clean_request(self, messages: List[Dict[str, Any]], system_prompt: str = None, model_provider: str = None) -> Dict[str, Any]:
		"""
		Cleans the system prompt and delegates message encoding to the specific provider's method.
		"""
		_system_prompt = ""
		if isinstance(system_prompt, str) and str(system_prompt).strip():
			_system_prompt = str(system_prompt).strip()

		# The main change is here: We no longer process the messages in the base client.
		# We pass the original, untouched messages list directly to the provider-specific
		# _encoded_messages method, which knows how to handle special types like images.
		encoded_messages = self._encoded_messages(messages)

		return {
			"messages": encoded_messages,
			"system_prompt": _system_prompt
		}

	def _decode_jresponse(self, response: Dict[str, Any], raise_exception: bool = False) -> Dict[str, Any]:
		"""
		Decode the response from the API.
		This method should be overridden by subclasses if needed.
		"""
		raise NotImplementedError("This method should be overridden by subclasses.")
