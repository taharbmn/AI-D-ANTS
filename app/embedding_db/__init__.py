"""
Database abstraction layer for AI-D-ANTS.

This module provides a unified interface for different database implementations,
allowing easy switching between database types while maintaining consistent API.
"""

import os
from typing import Dict, Any, Optional
from .base_db import BaseDBClient, DatabaseType, ChunkMetadata, QueryResult
from .base_db import DatabaseError, ConnectionError, SchemaError, QueryError
from app.utils.utils import get_local_data_dir

# Database client registry
_DB_CLIENTS: Dict[DatabaseType, type] = {}


def register_db_client(db_type: DatabaseType, client_class: type) -> None:
    """
    Register a database client implementation.
    
    Args:
        db_type: Database type enum
        client_class: Client class implementing BaseDBClient
    """
    if not issubclass(client_class, BaseDBClient):
        raise ValueError(f"Client class must inherit from BaseDBClient")
    
    _DB_CLIENTS[db_type] = client_class


def get_db_client(
    db_type: DatabaseType, 
    connection_string: str, 
    **kwargs
) -> BaseDBClient:
    """
    Factory function to create and return appropriate database client.
    
    Args:
        db_type: Type of database to connect to
        connection_string: Database connection string
        **kwargs: Additional database-specific parameters
        
    Returns:
        Configured database client instance
        
    Raises:
        ValueError: If database type is not supported
        ConnectionError: If connection fails
    """
    if db_type not in _DB_CLIENTS:
        raise ValueError(f"Unsupported database type: {db_type.value}")
    
    client_class = _DB_CLIENTS[db_type]
    return client_class(connection_string, **kwargs)


def setup_database(
    db_type: DatabaseType, 
    connection_string: str, 
    create_schema: bool = True,
    **kwargs
) -> BaseDBClient:
    """
    Initialize database with required schemas.
    
    Args:
        db_type: Type of database to setup
        connection_string: Database connection string
        create_schema: Whether to create the schema automatically
        **kwargs: Additional database-specific parameters
        
    Returns:
        Configured and initialized database client
        
    Raises:
        ConnectionError: If connection fails
        SchemaError: If schema creation fails
    """
    try:
        client = get_db_client(db_type, connection_string, **kwargs)
        client.connect()
        
        if create_schema:
            client.create_schema()
            
        return client
        
    except Exception as e:
        raise ConnectionError(f"Failed to setup database: {str(e)}")


def get_default_connection_string(db_type: DatabaseType) -> str:
    """
    Get default connection string for a database type.
    
    Args:
        db_type: Database type
        
    Returns:
        Default connection string
    """
    default_path = get_local_data_dir() + "/db/"
    defaults = {
        DatabaseType.DUCKDB: os.path.join(default_path, "chunks.duckdb")
    }
    
    return defaults.get(db_type, "")


def auto_register_clients() -> None:
    """Automatically register available database clients."""
    try:
        from .duckdb_client import DuckDBClient
        register_db_client(DatabaseType.DUCKDB, DuckDBClient)
    except ImportError:
        pass


# Auto-register available clients on module import
auto_register_clients()


# Configuration management
class DatabaseConfig:
    """Database configuration manager."""
    
    @classmethod
    def from_env(cls) -> Dict[str, Any]:
        """
        Load database configuration from environment variables.
        
        Returns:
            Configuration dictionary
        """
        return {
            'db_type': DatabaseType(os.getenv('DB_TYPE', 'duckdb')),
            'connection_string': os.getenv('DB_CONNECTION_STRING', ''),
            'pool_size': int(os.getenv('DB_POOL_SIZE', '5')),
            'timeout': int(os.getenv('DB_TIMEOUT', '30')),
            'auto_create_schema': os.getenv('DB_AUTO_CREATE_SCHEMA', 'true').lower() == 'true'
        }
    
    @classmethod
    def get_client_from_env(cls) -> BaseDBClient:
        """
        Create database client from environment configuration.
        
        Returns:
            Configured database client
        """
        config = cls.from_env()
        db_type = config.pop('db_type')
        connection_string = config.pop('connection_string')
        
        if not connection_string:
            connection_string = get_default_connection_string(db_type)
        
        return get_db_client(db_type, connection_string, **config)


# Export public API
__all__ = [
    'BaseDBClient',
    'DatabaseType', 
    'ChunkMetadata',
    'QueryResult',
    'DatabaseError',
    'ConnectionError', 
    'SchemaError',
    'QueryError',
    'get_db_client',
    'setup_database',
    'register_db_client',
    'get_default_connection_string',
    'DatabaseConfig'
]