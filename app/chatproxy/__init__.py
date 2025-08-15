"""
	- Our Stardard API Client Request Format:
		{
			"messages": [
				{
					"role"   : "user",
					"content": [
						{"text": "Hello, how can I assist you today?"}
					]
				}
			],
			"system_prompt": "You are a helpful assistant."
		}
	- Our Standard API Client Response Format:
		{
			"status"  : 200,
			"success" : true,
			"error"   : "",
			"response": {
				"messages": [
					{
						"role"   : "assistant",
						"content": [
							{"text": "Hello, how can I assist you today?"}
						]
					}
				]
			}
		}
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
import asyncio
from dotenv import load_dotenv
from typing import List, Dict, Any
from app.chatproxy.base_client      import BaseClient
from app.chatproxy.ollama_client    import OllamaClient
from app.chatproxy.dbx_client import DatabricksModel

logger = logging.getLogger(__name__)
load_dotenv()

class ChatProxyClient(BaseClient):
	def __init__(self, base: str = None, **kwargs):
		base = str(base).strip().lower()
		logger.debug(f"Initializing ChatProxyClient with base: {base}")
		if ("databricks" in base):
			logger.debug(f"Initializing DatabricksModel with base: {base}")
			self._client = DatabricksModel(**kwargs)
		elif ("ollama" in base):
			logger.debug(f"Initializing OllamaClient with base: {base}")
			self._client = OllamaClient(**kwargs)
		else:
			raise ValueError(f"Unsupported base client: {base}")
		
	def name(self) -> str:
		"""
		Return the name of the underlying client.
		This method should be overridden by subclasses if needed.
		"""
		return self._client.__class__.__name__

	async def send(self, messages: List[Dict[str, Any]], system_prompt: str = None, raise_exception: bool = False, **kwargs) -> Dict[str, Any]:
		"""
		Send messages to the underlying client (e.g., GeminiClient or BedrockClient).
		This method should be overridden by subclasses if needed.
		"""
		return await self._client.send(messages, system_prompt, raise_exception, **kwargs)
		
	def ping(self, raise_exception: bool = False) -> bool:
		"""
		Ping the underlying client to check if it's reachable.
		This method should be overridden by subclasses if needed.
		"""
		return self._client.ping(raise_exception = raise_exception)
	
	def __str__(self):
		"""
		Return a string representation of the ChatProxyClient.
		This method should be overridden by subclasses if needed.
		"""
		return f"ChatProxyClient(base={self._client.__class__.__name__})"
	
	def __repr__(self):
		"""
		Return a string representation of the ChatProxyClient for debugging.
		This method should be overridden by subclasses if needed.
		"""
		return f"ChatProxyClient(base={self._client.__class__.__name__})"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

async def main():

	client = ChatProxyClient(
		base = 'ollama'
	)

	rsp = await client.send(
		messages = [
			{
				'role'   : 'user',
				'content': [
					{'text': 'Hi bedrock, how are you?'},
				]
			}
		],
		system_prompt = 'You are a helpful assistant.'
	)
	print (json.dumps(rsp, indent=4))

# --- Run the asynchronous main function ---
if __name__ == "__main__":
    asyncio.run(main())