import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Application configuration management.
    Handles environment variables and default settings.
    """
    
    # Databricks Configuration
    DATABRICKS_TOKEN: str = os.environ.get('DATABRICKS_TOKEN', '')
    DATABRICKS_BASE_URL: str = os.environ.get('DATABRICKS_BASE_URL', '')
    DATABRICKS_DEFAULT_MODEL: str = os.environ.get(
        'DATABRICKS_DEFAULT_MODEL', 
        'databricks-meta-llama-3-3-70b-instruct'
    )
    
    # AWS Configuration (for S3 operations)
    AWS_REGION: str = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID: str = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY: str = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    
    # Application Settings
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    DEBUG: bool = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    # API Settings
    API_TIMEOUT: int = int(os.environ.get('API_TIMEOUT', '30'))
    MAX_RETRIES: int = int(os.environ.get('MAX_RETRIES', '3'))
    
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