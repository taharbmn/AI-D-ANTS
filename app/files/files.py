import os
import io
import sys
import logging
import pandas as pd
import fastparquet
from deltalake import DeltaTable
from dotenv    import load_dotenv
from app.utils.utils import (
    get_s3_client,
    parse_bucket_url,
    get_local_data_dir
)

# Load environment variables once at module level
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Also create a console handler to ensure logs show up
formatter       = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class FileReader:
    """Class to read files from S3 or local storage."""
    def __init__(self, file_path: str, *args, **kwargs):
        file_path = self._clean_file_path(file_path)
        [
            self._schema,
            self._bucket_name,
            self._relative_path
        ] = parse_bucket_url(file_path)
        self._dataframe    = None
        self._file_type    = None
        self._file_content = None
        self.get_file_type()
        if str(file_path).strip().lower().endswith("/_delta_log"):
            self._file_type = "delta"
        
    @property
    def content(self):
        """Get the content of the file."""
        if self._file_content is None:
            self._file_content = self.readfile(self._schema + "://" + self._bucket_name + "/" + self._relative_path)
        return self._file_content
    
    def __str__(self):
        return f"<FileReader src='{self._schema}://{self._bucket_name}/{self._relative_path}' type='{self._file_type}'>"
    
    def __repr__(self):
        return self.__str__()
    
    def get_file_type(self):
        # TODO: use good method to determine file type
        if self._file_type:
            return self._file_type
        name = self._relative_path.strip().lower()
        if name.endswith(".csv"):
            self._file_type = "csv"
        elif name.endswith(".xlsx") or name.endswith(".xls"):
            self._file_type = "xlsx"
        elif name.endswith(".parquet"):
            self._file_type = "parquet"
        elif name.endswith(".json"):
            self._file_type = "json"
        elif name.endswith(".pdf"):
            self._file_type = "pdf"
        return self._file_type

    def _clean_file_path(self, file_path: str) -> str:
        """Clean and validate the file path."""
        if (not file_path) or (not isinstance(file_path, str)):
            raise ValueError("File path must be a non-empty string.")
        file_path = str(file_path).strip()
        if (".." in file_path):
            raise ValueError("Invalid Path: File path cannot contain '..'")
        if not file_path:
            raise ValueError("File path cannot be empty.")
        if file_path.startswith("/"):
            file_path = "file://" + file_path
        return file_path

    @property
    def dataframe(self):
        """Get the DataFrame representation of the file."""
        if self._dataframe is None:
            self._dataframe = self.read_dataframe()
        return self._dataframe

    def _read_dataframe_callback(self, callback, *args, **kwargs):
        if self._dataframe is None:
            self._dataframe = callback( io.BytesIO(self.content), *args, **kwargs)
        return self._dataframe

    def read_csv_dataframe(self):
        return (self._read_dataframe_callback(pd.read_csv))

    def read_xlsx_dataframe(self):
        return (self._read_dataframe_callback(pd.read_excel))

    def read_parquet_dataframe(self):
        return (self._read_dataframe_callback(pd.read_parquet))

    def read_json_dataframe(self):
        return (self._read_dataframe_callback(pd.read_json))

    def read_pdf_dataframe(self):
        return (self._read_dataframe_callback(pd.read_pdf))

    def read_delta_dataframe(self):
        return (self._read_dataframe_callback(DeltaTable).to_pandas())

    def read_dataframe(self):
        """Read a file into a pandas DataFrame based on the file type."""
        if self._file_type == "csv":
            return self.read_csv_dataframe()
        elif self._file_type == "xlsx":
            return self.read_xlsx_dataframe()
        elif self._file_type == "parquet":
            return self.read_parquet_dataframe()
        elif self._file_type == "json":
            return self.read_json_dataframe()
        elif self._file_type == "pdf":
            return self.read_pdf_dataframe()
        elif self._file_type == "delta":
            return self.read_delta_dataframe()
        raise ValueError(f"Unsupported file type: {self._file_type}. Supported types are: csv, xlsx, parquet, json, pdf.")

    @staticmethod
    def readfile(path: str) -> str:
        [
            schema,
            bucket_name,
            relative_path
        ] = parse_bucket_url(path)

        if schema == "s3":
            _s3_obj = get_s3_client().get_object(Bucket = bucket_name, Key = relative_path)
            return _s3_obj['Body'].read()

        if schema == "local-data":
            newpath = os.path.join(get_local_data_dir(), bucket_name, relative_path)
        elif schema == "file":
            newpath = os.path.join("/", bucket_name, relative_path)
        else:
            raise ValueError("Invalid file path.")

        if not os.path.exists(newpath):
            raise FileNotFoundError(f"File not found: {newpath}")

        with open(newpath, 'rb') as file:
            return file.read()

        raise ValueError("Invalid file path.")