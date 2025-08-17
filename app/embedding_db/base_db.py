from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class DatabaseType(Enum):
    """Supported database types."""
    DUCKDB = "duckdb"
    SQLITE = "sqlite"
    POSTGRES = "postgres"


@dataclass
class ChunkMetadata:
    """Metadata for a data chunk."""
    chunk_id: str
    source_file: str
    file_type: str
    chunk_index: int
    total_chunks: int
    row_start: int
    row_end: int
    headers: List[str]
    json_metadata: Optional[Dict[str, Any]] = None
    file_size: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class QueryResult:
    """Result of a database query."""
    data: List[Dict[str, Any]]
    count: int
    metadata: Optional[Dict[str, Any]] = None


class BaseDBClient(ABC):
    """Abstract base class for database clients."""
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize database client.
        
        Args:
            connection_string: Database connection string
            **kwargs: Additional database-specific parameters
        """
        self.connection_string = connection_string
        self.connection = None
        self.config = kwargs
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def create_schema(self) -> None:
        """Create required database schema/tables."""
        pass
    
    @abstractmethod
    def insert_chunk(self, chunk_data: Dict[str, Any], metadata: ChunkMetadata) -> str:
        """
        Insert a single data chunk with metadata.
        
        Args:
            chunk_data: The actual data content
            metadata: Chunk metadata
            
        Returns:
            Unique identifier for the inserted chunk
        """
        pass
    
    @abstractmethod
    def insert_chunks(self, chunks: List[Dict[str, Any]], metadata_list: List[ChunkMetadata]) -> List[str]:
        """
        Batch insert multiple chunks.
        
        Args:
            chunks: List of data chunks
            metadata_list: List of corresponding metadata
            
        Returns:
            List of unique identifiers for inserted chunks
        """
        pass
    
    @abstractmethod
    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """
        Execute a raw SQL query.
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        pass
    
    @abstractmethod
    def get_chunks_by_metadata(self, filters: Dict[str, Any], limit: Optional[int] = None) -> QueryResult:
        """
        Retrieve chunks based on metadata filters.
        
        Args:
            filters: Metadata filters (e.g., {'source_file': 'data.csv', 'file_type': 'csv'})
            limit: Maximum number of results
            
        Returns:
            Filtered chunks
        """
        pass
    
    @abstractmethod
    def search_content(self, search_term: str, filters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """
        Search within chunk content.
        
        Args:
            search_term: Text to search for
            filters: Optional metadata filters
            
        Returns:
            Matching chunks
        """
        pass
    
    @abstractmethod
    def delete_chunks_by_source(self, source_file: str) -> int:
        """
        Delete all chunks from a specific source file.
        
        Args:
            source_file: Source file path
            
        Returns:
            Number of deleted chunks
        """
        pass
    
    @abstractmethod
    def get_source_files(self) -> List[str]:
        """
        Get list of all source files in the database.
        
        Returns:
            List of source file paths
        """
        pass
    
    @abstractmethod
    def get_file_stats(self, source_file: str) -> Dict[str, Any]:
        """
        Get statistics for a specific source file.
        
        Args:
            source_file: Source file path
            
        Returns:
            File statistics (chunk count, total rows, etc.)
        """
        pass
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class ConnectionError(DatabaseError):
    """Database connection error."""
    pass


class SchemaError(DatabaseError):
    """Database schema error."""
    pass


class QueryError(DatabaseError):
    """Database query error."""
    pass