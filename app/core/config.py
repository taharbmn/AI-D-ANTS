import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import pathlib

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
    DATABASE_URL: str = os.environ.get('DATABASE_URL', '')
    DOCKER_DATABASE_URL: Optional[str] = os.environ.get('DOCKER_DATABASE_URL')

    # PostgreSQL specific variables (used by Docker Compose)
    POSTGRES_DB: Optional[str] = os.environ.get('POSTGRES_DB')
    POSTGRES_USER: Optional[str] = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD: Optional[str] = os.environ.get('POSTGRES_PASSWORD')

    # Security Configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY', '')
    ALGORITHM: str = os.environ.get('ALGORITHM', 'HS256')

    # Application Configuration
    ALLOWED_HOSTS: str = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')

    # Databricks Configuration
    DATABRICKS_TOKEN: str = os.environ.get('DATABRICKS_TOKEN', '')
    DATABRICKS_BASE_URL: str = os.environ.get('DATABRICKS_BASE_URL', '')
    DATABRICKS_DEFAULT_MODEL: str = os.environ.get(
        'DATABRICKS_DEFAULT_MODEL',
        'databricks-meta-llama-3-3-70b-instruct'
    )

    # AWS Configuration (for S3 operations)
    AWS_REGION: str = os.environ.get('AWS_REGION', '')
    AWS_ACCESS_KEY_ID: str = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY: str = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

    # Application Settings
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    DEBUG: bool = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

    # API Settings
    API_TIMEOUT: int = int(os.environ.get('API_TIMEOUT', '30'))
    MAX_RETRIES: int = int(os.environ.get('MAX_RETRIES', '3'))

    MODEL_TYPE: str = os.environ.get('MODEL_TYPE', '')
    OLLAMA_DEFAULT_MODEL: str = os.environ.get('OLLAMA_DEFAULT_MODEL', 'qwen3:1.7b')

    # Embedding Database Configuration
    EMBEDDING_CHUNK_SIZE: int = int(os.environ.get('EMBEDDING_CHUNK_SIZE', '1000'))

    if MODEL_TYPE.lower() == 'ollama':
        client_type: str = "ollama"
        model_id: str = OLLAMA_DEFAULT_MODEL
    elif MODEL_TYPE.lower() == 'databricks':
        client_type: str = "databricks"
        model_id: str = DATABRICKS_DEFAULT_MODEL
    else:
        raise ValueError(f"Unsupported MODEL_TYPE: {MODEL_TYPE}. Supported types are 'ollama' and 'databricks'.")


    @property
    def AGENT_CONFIGS(self) -> dict:
        return {
            "brain": {
                "primary": {
                    "client_type": self.client_type,
                    "model_id": self.model_id,
                    "temperature": 0.1,
                    "max_tokens": 5000
                },
                "system_prompt_path": "app/system_prompt/brain.md"
            },
            "data_expert": {
                "primary": {
                    "client_type": self.client_type,
                    "model_id": self.model_id,
                    "temperature": 0.1,
                    "max_tokens": 5000
                },
                "system_prompt_path": "app/system_prompt/data_eng.md"
            },
            "metadata": {
                "primary": {
                    "client_type": self.client_type,
                    "model_id": self.model_id,
                    "temperature": 0.1,
                    "max_tokens": 5000
                },
                "system_prompt_path": "app/system_prompt/metadata.md"
            }
        }

    @classmethod
    def get_databricks_config(cls) -> Dict[str, Any]:
        """
        Get Databricks-specific configuration.

        Returns:
            Dictionary with Databricks configuration
        """
        return {
            'token': cls.DATABRICKS_TOKEN,
            'base_url': cls.DATABRICKS_BASE_URL,
            'default_model': cls.DATABRICKS_DEFAULT_MODEL,
            'timeout': cls.API_TIMEOUT,
            'max_retries': cls.MAX_RETRIES
        }

    @classmethod
    def get_aws_config(cls) -> Dict[str, Any]:
        """
        Get AWS-specific configuration.

        Returns:
            Dictionary with AWS configuration
        """
        return {
            'region': cls.AWS_REGION,
            'access_key_id': cls.AWS_ACCESS_KEY_ID,
            'secret_access_key': cls.AWS_SECRET_ACCESS_KEY
        }

    @classmethod
    def validate_databricks_config(cls) -> bool:
        """
        Validate that required Databricks configuration is present.

        Returns:
            True if configuration is valid, False otherwise
        """
        return bool(cls.DATABRICKS_TOKEN and cls.DATABRICKS_BASE_URL)

    @classmethod
    def validate_aws_config(cls) -> bool:
        """
        Validate that required AWS configuration is present.

        Returns:
            True if configuration is valid, False otherwise
        """
        return bool(cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY)

# Create a global config instance
config = Config()


# Global variables for caching
system_prompts: Dict[str, str] = {}
client_cache: Dict[str, Any] = {}


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

def initialize_cache_client() -> Dict[str, Any]:
    """
    Initialize and return a client cache.

    Returns:
        Dictionary with initialized clients
    """
    global client_cache
    import logging
    logger = logging.getLogger(__name__)

    # Clear existing cache
    client_cache.clear()
    client_cache.update({
        'databricks': None,
        'ollama': None
    })

    logger.info(f"Initializing client cache with client_type: {config.client_type}")

    if config.client_type == 'databricks':
        if config.validate_databricks_config():
            
            kwargs = {
                'model_name': config.model_id,
                'base_url': config.DATABRICKS_BASE_URL
            }
            client_cache['databricks'] = ChatProxyClient(base="databricks",**kwargs)
            logger.info("Databricks client initialized successfully")
        else:
            raise ValueError("Invalid Databricks configuration")

    elif config.client_type == 'ollama':
        kwargs = {
            'model_name': config.model_id
        }
        client_cache['ollama'] = ChatProxyClient(base="ollama", **kwargs)
        logger.info(f"Ollama client initialized successfully with model: {config.model_id}")

    logger.info(f"Client cache initialized: {list(client_cache.keys())}")
    return client_cache
