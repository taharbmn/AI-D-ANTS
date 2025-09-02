import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import pathlib

from app.chatproxy.ollama_client import OllamaClient

# Get the root directory of the project (parent of app directory)
root_dir = pathlib.Path(__file__).parent.parent.parent
env_path = root_dir / ".env"
from app.chatproxy import ChatProxyClient
# Load environment variables from the .env file
load_dotenv(dotenv_path=env_path)


class Config:
    """
    Application configuration management.
    Handles environment variables and default settings.
    """

    # Database Configuration
    DATABASE_URL: str = os.environ.get('DATABASE_URL', 'sqlite:///./app_database.db')
    DOCKER_DATABASE_URL: Optional[str] = os.environ.get('DOCKER_DATABASE_URL')

    # Security Configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY', '')
    ALGORITHM: str = os.environ.get('ALGORITHM', 'HS256')

    # Application Configuration
    ALLOWED_HOSTS: str = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')


    # Embedding Database Configuration
    EMBEDDING_CHUNK_SIZE: int = int(os.environ.get('EMBEDDING_CHUNK_SIZE', '1000'))

    @property
    def AGENT_CONFIGS(self) -> dict:
        return {
            "brain": {
                "system_prompt_path": "app/system_prompt/brain.md"
            },
            "data_expert": {
                "system_prompt_path": "app/system_prompt/data_eng.md"
            },
            "metadata": {
                "system_prompt_path": "app/system_prompt/metadata.md"
            }
        }

    
# Create a global config instance
config = Config()


# Global variables for caching
system_prompts: Dict[str, str] = {}


def initialize_config() -> Config:
    """
    Initialize and return the global configuration instance.

    Returns:
        Config: The initialized configuration instance
    """
    global config
    return config

def load_system_prompts() -> dict[str, str]:
    """Load all system prompts into memory at startup"""
    global system_prompts
    import logging
    logger = logging.getLogger(__name__)
    system_prompts.clear()  # Clear existing prompts

    for agent_name, agent_config in config.AGENT_CONFIGS.items():
         prompt_path = agent_config.get("system_prompt_path")
         if prompt_path:
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    logger.info(f"Loaded system prompt for agent '{agent_name}' from {prompt_path}")
                    system_prompts[agent_name] = f.read()
            except FileNotFoundError:
                raise RuntimeError(f"System prompt file not found for agent '{agent_name}': {prompt_path}")
            except IOError as e:
                raise RuntimeError(f"Error reading system prompt for agent '{agent_name}': {e}")

    return system_prompts


def ai_client(model_type: str) -> Dict[str, Any]:
    """
    Initialize and return the client for the specified model type.

    Args:
        model_type (str): The type of model to initialize

    Returns:
        Dict[str, Any]: The initialized client
    """

    if model_type == "ollama":
        model_name = os.environ.get("OLLAMA_DEFAULT_MODEL")
        if not model_name:
            raise ValueError("OLLAMA_DEFAULT_MODEL environment variable is not set")
        kwargs = {
            "model_name": model_name
            }
        client = ChatProxyClient(base="ollama", **kwargs)
    elif model_type == "databricks":
        model_name = os.environ.get("DATABRICKS_DEFAULT_MODEL")
        if not model_name:
            raise ValueError("OLLAMA_DEFAULT_MODEL environment variable is not set")

        base_url = os.environ.get("DATABRICKS_BASE_URL")
        if not base_url:
            raise ValueError("DATABRICKS_BASE_URL environment variable is not set")

        token = os.environ.get("DATABRICKS_TOKEN")
        if not token:
            raise ValueError("DATABRICKS_TOKEN environment variable is not set")

        kwargs = {
            "model_name": model_name,
            "base_url": base_url,
            "token": token
            }
        client = ChatProxyClient(base="databricks", **kwargs)
    else:
        raise ValueError(f"Unsupported model type: {model_type}, expected 'ollama' or 'databricks'")

    return client
