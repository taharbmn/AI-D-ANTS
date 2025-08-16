import duckdb
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_db import (
    BaseDBClient, 
    ChunkMetadata, 
    QueryResult, 
    DatabaseError, 
    ConnectionError, 
    SchemaError, 
    QueryError
)


class DuckDBClient(BaseDBClient):
    """DuckDB implementation of the database client."""
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize DuckDB client.
        
        Args:
            connection_string: Path to DuckDB database file
            **kwargs: Additional parameters (read_only, config, etc.)
        """
        super().__init__(connection_string, **kwargs)
        self.read_only = kwargs.get('read_only', False)
        self.config = kwargs.get('config', {})
    
    def connect(self) -> None:
        """Establish connection to DuckDB database."""
        try:
            # Ensure directory exists
            db_dir = os.path.dirname(self.connection_string)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Connect to DuckDB
            self.connection = duckdb.connect(
                database=self.connection_string,
                read_only=self.read_only,
                config=self.config
            )
            
            # Optimize DuckDB for analytics workloads
            self._configure_database()
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to DuckDB: {str(e)}")
    
    def close(self) -> None:
        """Close DuckDB connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def _configure_database(self) -> None:
        """Configure DuckDB for optimal performance."""
        if not self.connection:
            return
        
        # Enable parallel processing
        self.connection.execute("SET threads TO 4")
        
        # Optimize memory usage
        self.connection.execute("SET memory_limit = '2GB'")
        
        # Enable JSON extension for better JSON handling
        try:
            self.connection.execute("INSTALL json")
            self.connection.execute("LOAD json")
        except:
            pass  # JSON extension might already be loaded
    
    def create_schema(self) -> None:
        """Create required tables and indexes."""
        if not self.connection:
            raise SchemaError("No database connection")
        
        try:
            # Create chunks table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id VARCHAR PRIMARY KEY,
                    chunk_id VARCHAR NOT NULL,
                    source_file VARCHAR NOT NULL,
                    file_type VARCHAR NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    total_chunks INTEGER NOT NULL,
                    row_start INTEGER NOT NULL,
                    row_end INTEGER NOT NULL,
                    headers JSON NOT NULL,
                    content JSON NOT NULL,
                    json_metadata JSON,
                    file_size BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(chunk_id)
                )
            """)
            
            # Create indexes for better query performance
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_source_file 
                ON chunks(source_file)
            """)
            
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_file_type 
                ON chunks(file_type)
            """)
            
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index 
                ON chunks(chunk_index)
            """)
            
            self.connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_created_at 
                ON chunks(created_at)
            """)
            
        except Exception as e:
            raise SchemaError(f"Failed to create schema: {str(e)}")
    
    def insert_chunk(self, chunk_data: Dict[str, Any], metadata: ChunkMetadata) -> str:
        """Insert a single data chunk with metadata."""
        if not self.connection:
            raise DatabaseError("No database connection")
        
        try:
            # Generate unique ID if not provided
            record_id = str(uuid.uuid4())
            
            # Prepare data
            insert_data = {
                'id': record_id,
                'chunk_id': metadata.chunk_id,
                'source_file': metadata.source_file,
                'file_type': metadata.file_type,
                'chunk_index': metadata.chunk_index,
                'total_chunks': metadata.total_chunks,
                'row_start': metadata.row_start,
                'row_end': metadata.row_end,
                'headers': json.dumps(metadata.headers),
                'content': json.dumps(chunk_data),
                'json_metadata': json.dumps(metadata.json_metadata) if metadata.json_metadata else None,
                'file_size': metadata.file_size,
                'created_at': metadata.created_at or datetime.now().isoformat()
            }
            
            # Insert data
            self.connection.execute("""
                INSERT INTO chunks (
                    id, chunk_id, source_file, file_type, chunk_index, 
                    total_chunks, row_start, row_end, headers, content, 
                    json_metadata, file_size, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, list(insert_data.values()))
            
            return record_id
            
        except Exception as e:
            raise QueryError(f"Failed to insert chunk: {str(e)}")
    
    def insert_chunks(self, chunks: List[Dict[str, Any]], metadata_list: List[ChunkMetadata]) -> List[str]:
        """Batch insert multiple chunks."""
        if not self.connection:
            raise DatabaseError("No database connection")
        
        if len(chunks) != len(metadata_list):
            raise ValueError("Chunks and metadata lists must have the same length")
        
        try:
            record_ids = []
            batch_data = []
            
            for chunk_data, metadata in zip(chunks, metadata_list):
                record_id = str(uuid.uuid4())
                record_ids.append(record_id)
                
                batch_data.append([
                    record_id,
                    metadata.chunk_id,
                    metadata.source_file,
                    metadata.file_type,
                    metadata.chunk_index,
                    metadata.total_chunks,
                    metadata.row_start,
                    metadata.row_end,
                    json.dumps(metadata.headers),
                    json.dumps(chunk_data),
                    json.dumps(metadata.json_metadata) if metadata.json_metadata else None,
                    metadata.file_size,
                    metadata.created_at or datetime.now().isoformat()
                ])
            
            # Batch insert
            self.connection.executemany("""
                INSERT INTO chunks (
                    id, chunk_id, source_file, file_type, chunk_index, 
                    total_chunks, row_start, row_end, headers, content, 
                    json_metadata, file_size, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch_data)
            
            return record_ids
            
        except Exception as e:
            raise QueryError(f"Failed to batch insert chunks: {str(e)}")
    
    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a raw SQL query."""
        if not self.connection:
            raise DatabaseError("No database connection")
        
        try:
            if params:
                result = self.connection.execute(sql, list(params.values()))
            else:
                result = self.connection.execute(sql)
            
            # Fetch results
            rows = result.fetchall()
            columns = [desc[0] for desc in result.description] if result.description else []
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in rows]
            
            return QueryResult(
                data=data,
                count=len(data),
                metadata={'columns': columns}
            )
            
        except Exception as e:
            raise QueryError(f"Query execution failed: {str(e)}")
    
    def get_chunks_by_metadata(self, filters: Dict[str, Any], limit: Optional[int] = None) -> QueryResult:
        """Retrieve chunks based on metadata filters."""
        if not self.connection:
            raise DatabaseError("No database connection")
        
        try:
            # Build WHERE clause
            where_conditions = []
            params = []
            
            for key, value in filters.items():
                if key in ['source_file', 'file_type', 'chunk_id']:
                    where_conditions.append(f"{key} = ?")
                    params.append(value)
                elif key == 'chunk_index':
                    where_conditions.append("chunk_index = ?")
                    params.append(value)
                elif key == 'created_after':
                    where_conditions.append("created_at > ?")
                    params.append(value)
                elif key == 'created_before':
                    where_conditions.append("created_at < ?")
                    params.append(value)
            
            # Build query
            sql = "SELECT * FROM chunks"
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
            
            sql += " ORDER BY source_file, chunk_index"
            
            if limit:
                sql += f" LIMIT {limit}"
            
            return self.query(sql, dict(enumerate(params)) if params else None)
            
        except Exception as e:
            raise QueryError(f"Failed to get chunks by metadata: {str(e)}")
    
    def search_content(self, search_term: str, filters: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Search within chunk content."""
        if not self.connection:
            raise DatabaseError("No database connection")
        
        try:
            # Build base query with content search
            sql = """
                SELECT * FROM chunks 
                WHERE content::VARCHAR LIKE ?
            """
            params = [f"%{search_term}%"]
            
            # Add additional filters
            if filters:
                for key, value in filters.items():
                    if key in ['source_file', 'file_type']:
                        sql += f" AND {key} = ?"
                        params.append(value)
            
            sql += " ORDER BY source_file, chunk_index"
            
            return self.query(sql, dict(enumerate(params)))
            
        except Exception as e:
            raise QueryError(f"Content search failed: {str(e)}")
    
    def delete_chunks_by_source(self, source_file: str) -> int:
        """Delete all chunks from a specific source file."""
        if not self.connection:
            raise DatabaseError("No database connection")
        
        try:
            result = self.connection.execute(
                "DELETE FROM chunks WHERE source_file = ?", 
                [source_file]
            )
            return result.rowcount if hasattr(result, 'rowcount') else 0
            
        except Exception as e:
            raise QueryError(f"Failed to delete chunks: {str(e)}")
    
    def get_source_files(self) -> List[str]:
        """Get list of all source files in the database."""
        try:
            result = self.query("SELECT DISTINCT source_file FROM chunks ORDER BY source_file")
            return [row['source_file'] for row in result.data]
            
        except Exception as e:
            raise QueryError(f"Failed to get source files: {str(e)}")
    
    def get_file_stats(self, source_file: str) -> Dict[str, Any]:
        """Get statistics for a specific source file."""
        try:
            result = self.query("""
                SELECT 
                    COUNT(*) as chunk_count,
                    MAX(total_chunks) as expected_chunks,
                    MIN(row_start) as min_row,
                    MAX(row_end) as max_row,
                    file_type,
                    file_size,
                    MIN(created_at) as first_created,
                    MAX(created_at) as last_created
                FROM chunks 
                WHERE source_file = ?
                GROUP BY source_file, file_type, file_size
            """, {0: source_file})
            
            if result.data:
                return result.data[0]
            else:
                return {}
                
        except Exception as e:
            raise QueryError(f"Failed to get file stats: {str(e)}")