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
	It should be extended by specific API clients like Databricks models.
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
	
	def _clean_request(self, messages: List[Dict[str, Any]], system_prompt: str = None) -> Dict[str, Any]:
		_messages      = []
		_system_prompt = ""
		if isinstance(system_prompt, str) and str(system_prompt).strip():
			_system_prompt = str(system_prompt).strip()
		for message in messages:
			if not isinstance(message, dict):
				logger.warning(f"Skipping non-dict message: {message}")
				continue
			role    = message.get('role', 'user').strip().lower()
			content = message.get('content', [])
			if role not in ['user', 'assistant']:
				logger.warning(f"Skipping message with invalid role: {message}")
				continue
			if not content or not isinstance(content, list):
				logger.warning(f"Skipping message with no content or invalid content type: {message}")
				continue
			_content = []
			for part in content:
				text = None
				if isinstance(part, dict) and 'text' in part and part['text'] is not None:
					text = str(part['text']).strip()
				elif isinstance(part, str) and part is not None:
					text = str(part).strip()
				if not text or not isinstance(text, str):
					logger.warning(f"Skipping content part without valid 'text': {part}")
					continue
				if text:
					_content.append({'text': text})
			if not _content:
				logger.warning(f"Skipping message with empty content: {message}")
				continue
			_messages.append({
				'role'   : role,
				'content': _content
			})
		return {
			"messages"     : self._encoded_messages(_messages),
			"system_prompt": _system_prompt
		}

	def _decode_jresponse(self, response: Dict[str, Any], raise_exception: bool = False) -> Dict[str, Any]:
		"""
		Decode the response from the API.
		This method should be overridden by subclasses if needed.
		"""
		raise NotImplementedError("This method should be overridden by subclasses.")