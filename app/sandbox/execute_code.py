import os
import sys

import baisstools
baisstools.insert_syspath(__file__, matcher = [r"^baiss_.*$"])

import io
import time
import uuid
import json
import boto3
import base64
import logging
import mimetypes
import traceback
import contextlib
import numpy as np
import pandas as pd
import multiprocessing
# import awswrangler as wr
from dotenv import load_dotenv
from typing import Dict, Any
from app.sandbox.sandbox import PythonSandbox
from app.parser.parsing import clear_varname, clear_varname_dict
from app.files.files import FileReader

# Load environment variables once at module level
load_dotenv()

SECURE_PACKAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secure-packages")
REPOSITORY_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMEOUT_SECONDS    = 60

logger = logging.getLogger(__name__)

S3_READERS = {
    # "csv"    : wr.s3.read_csv,
    # "xlsx"   : wr.s3.read_excel,
    # "parquet": wr.s3.read_parquet,
    # "json"   : wr.s3.read_json,
}

LOCAL_READERS = {
    "csv"     : pd.read_csv,
    "xlsx"    : pd.read_excel,
    "parquet" : pd.read_parquet,
    "json"    : pd.read_json,
}

SAFE_MODULES = {
    "pandas"            : ["pd"],
    "numpy"             : ["np"],
    # "boto3"             : ["boto3"],
    # "awswrangler"       : ["wr"],
    # "matplotlib.pyplot" : ["plt"]
}

SAFE_FROM_MODULES = [
    "from app.sandbox.execute_code import read_pandas_dataFrame_from_source",
]

SAFE_BUILTINS = {
    '__builtins__': __builtins__,
    'print'       : print,
    'type'        : type,
    'len'         : len,
    'str'         : str,
    'int'         : int,
    'float'       : float,
    'list'        : list,
    'dict'        : dict,
    'tuple'       : tuple,
    'set'         : set,
    'range'       : range,
    'abs'         : abs,
    'round'       : round,
    'max'         : max,
    'min'         : min,
    'sum'         : sum,
    'sorted'      : sorted,
    'isinstance'  : isinstance,
    'Exception'   : Exception,
    '__import__'  : __import__,
}

def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.
    Parameters:
        filename (str): The name of the file.
    Returns:
        str: The file extension, or an empty string if no extension is found.
    """
    filename = filename.strip()
    while filename and filename[-1] in ["\\", "/", "."]:
        filename = filename[:-1].strip()
    if not filename:
        return ''
    basename = filename.split("/")[-1].strip()
    if not basename:
        return ''
    if not ('.' in basename):
        return ''
    return basename.split('.')[-1].strip().lower()

def get_file_type(filename: str) -> str:
    ext = get_file_extension(filename)
    if ext:
        return ext
    else:
        raise ValueError("File has no extension or is not a valid file type.")
    return "xlsx"
    # content_type, _ = mimetypes.guess_type(filename)
    # if content_type is None:
    #     content_type = 'text/plain'
    # if content_type == "text/plain":
    #     extension = get_file_extension(filename)
    #     if extension == "csv":
    #         return 'text/csv'
    #     elif extension == "json":
    #         return 'application/json'
    # return content_type

def _debug_savecode(response: str, code: str) -> str:

    logger.info(f"response = {response}")

    dirname  = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "out", str(uuid.uuid4()))
    os.makedirs(dirname, exist_ok = True)

    try:
        with open(os.path.join(dirname, "code.py"), "w") as fp:
            fp.write(str(code))
    except:
        pass
    try:
        with open(os.path.join(dirname, "response.json"), "w") as fp:
            fp.write( json.dumps(response, indent = 4) )
    except:
        pass

def _clean_python_code(python_code: str, target_file: str) -> str:

    readfuncs = []
    for i in range(len(python_code)):
        for funcname in ["read_pandas_dataFrame_from_source"]:
            if not (python_code[i:].startswith(funcname)):
                continue
            if not (python_code[i + len(funcname):].strip().startswith("(")):
                continue
            func_call = python_code[i:].split(")")[0] + ")"
            if not (func_call in python_code):
                continue
            readfuncs.append(func_call)
    for readfunc in readfuncs:
        python_code = python_code.replace(readfunc, f"read_pandas_dataFrame_from_source('{target_file}')")

    python_code  = python_code.replace("```python", "")
    python_code  = python_code.replace("`", "")
    _python_code = ""

    for line in python_code.split("\n"):
        if line.strip().startswith("import"):
            continue
        if line.strip().startswith("from"):
            continue

        _python_code += line + "\n"

    python_code = _python_code

    prefix = ""
    prefix = f"import sys\nsys.path.append('{SECURE_PACKAGE_DIR}')\n\n"

    for module_name, module_aslist in SAFE_MODULES.items():
        # prefix = prefix.strip() + f"\nimport {module_name}\n"
        for asname in module_aslist:
            prefix = prefix.strip() + f"\nimport {module_name} as {asname}\n"
        if module_name == "pandas":
            prefix = prefix.strip() + f"\npd.set_option('display.max_colwidth', None)\n" + f"\npd.set_option('display.width', None)\n" + f"\npd.set_option('display.max_columns', None)\n"

    local_safe_from_modules = SAFE_FROM_MODULES.copy()
    local_safe_from_modules.append(
        f"df_original = read_pandas_dataFrame_from_source('{target_file}')"
    )


    for fromline in local_safe_from_modules:
        prefix = prefix.strip() + f"\n{fromline.strip()}\n"

    return (prefix.strip() + "\n" + python_code.strip() + "\n")

def _worker_exec(code: str, result_queue: multiprocessing.Queue):
    session_globals = {
        '__builtins__': SAFE_BUILTINS,
    }
    stdout = io.StringIO()
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exec(code, session_globals)
        result_queue.put({
            "success": True,
            "stdout" : str(stdout.getvalue()).strip(),
            "stderr" : str(stderr.getvalue()).strip(),
            "error"  : None
        })
    except Exception as e:
        result_queue.put({
            "success": False,
            "stdout" : str(output.getvalue()).strip(),
            "stderr" : str(stderr.getvalue()).strip(),
            "error"  : f"{type(e).__name__}: {str(e)}\n{stderr.getvalue()}",
        })

def execute_python_code(**kwargs):
    kwargs = clear_varname_dict(kwargs)
    python_code      = str(kwargs.get("code", ""))
    data_source_file = str(kwargs.get("datasourcefile", ""))
    if not python_code:
        raise ValueError("No code provided for execution")
    if not data_source_file:
        raise ValueError("No data source file provided for execution")
    start_time = time.time()
    # logging.info(f"Executing Python code:\n{python_code}")
    for code in PythonSandbox(content = python_code).split():
        code = _clean_python_code(code, data_source_file)
        logger.info(f"\n\n{code}\n\n")
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target = _worker_exec,
            args   = (code, result_queue)
        )
        process.start()
        process.join(timeout = TIMEOUT_SECONDS)
        response = {}
        if process.is_alive():
            process.terminate()
            process.join()
            response = {
                "success": False,
                "stdout" : None,
                "stderr" : None,
                "error"  : f"Execution timed out after {TIMEOUT_SECONDS} seconds and was terminated.",
                "execution_time": TIMEOUT_SECONDS
            }
        elif process.exitcode == 0:
            if not result_queue.empty():
                result = result_queue.get()
                result["execution_time"] = f"{time.time() - start_time:.3f}s"
                response = result
            else:
                response = {
                    "success": False,
                    "stdout" : None,
                    "stderr" : None,
                    "error"  : "No result was returned from the execution process.",
                    "execution_time": f"{time.time() - start_time:.3f}s"
                }
        else:
            response = {
                "success": False,
                "stdout" : None,
                "stderr" : None,
                "error"  : f"Execution process crashed (exit code: {process.exitcode}).",
                "execution_time": f"{time.time() - start_time:.3f}s"
            }
        # _debug_savecode(response, code)
        if response["success"]:
            break
    return (response)

def read_file_from_source(
    source_path: str,
) -> pd.DataFrame:
    """
    Read file from source (S3 or local) using appropriate reader based on file type.
    Args:
        source_path: S3 or local path to the file (e.g., 's3://bucket/path/file.csv' or 'local-data://path/to/file.csv')
    Returns:
        Dict with status, result (DataFrame), error, and execution_time
    """
    start_time = time.perf_counter()
    try:
        fp = FileReader(source_path)
        logger.info(f"INFO: Reading from path: { source_path }")
        result = fp.read_dataframe()
        logger.info(f"successfull: {result } ")
        return {
            "status"        : True,
            "result"        : result,
            "error"         : None,
            "execution_time": f"{(time.perf_counter() - start_time) * 1000:.3f}ms"
        }
    except Exception as e:
        return {
            "status": False,
            "result": None,
            "error": f"{type(e).__name__}: {str(e)}",
            "execution_time": f"{(time.perf_counter() - start_time) * 1000:.3f}ms"
        }
    return

def read_pandas_dataFrame_from_source(source_path: str):

    response = read_file_from_source(source_path)
    if (not response["status"]) or response["error"]:
        return (None)
    return response["result"]

def get_file_metadata_from_source(source_path: str) -> Dict[str, Any]:
    """
    Get metadata of file from source (S3 or local).
    
    Args:
        source_path: S3 or local path to the file (e.g., 's3://bucket/path/file.csv' or 'local-data://path/to/file.csv')
        
    Returns:
        Dict with status, result (metadata), error, and execution_time
    """

    start_time = time.perf_counter()

    file_type = get_file_type(source_path)

    fileinfo = read_file_from_source(source_path)

    try:
        if (not fileinfo["status"]) or fileinfo["error"]:
            raise ValueError(fileinfo["error"])
        df = fileinfo["result"]
        metadata = {
            "file_info": {
                "path": source_path,
                "file_type": file_type,
                "shape": {
                    "rows"   : int(df.shape[0]),
                    "columns": int(df.shape[1])
                }
            },
            "columns": {
                "names" : df.columns.tolist(),
                "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
            },
            "sample_data": {
                "head": json.loads(df.head(3).to_json(orient='records')),
                "tail": json.loads(df.tail(3).to_json(orient='records'))
            }
        }
        return {
            "status"   : True,
            "metadata" : metadata,
            "error"    : None,
            "execution_time": f"{(time.perf_counter() - start_time) * 1000:.3f}ms"
        }
    except Exception as e:
        return {
            "status"  : False,
            "metadata": None,
            "error"   : f"Failed to get metadata for {source_path}. Error: {type(e).__name__}: {str(e)}",
            "execution_time": f"{(time.perf_counter() - start_time) * 1000:.3f}ms"
        }

def get_file_metadata(**kwargs):
    file_path = kwargs.get("file_path")
    result    = get_file_metadata_from_source( file_path )
    return result