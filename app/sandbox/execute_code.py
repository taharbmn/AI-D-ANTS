import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import io
import time
import uuid
import json
import boto3
import base64
import logging
import traceback
import contextlib
import numpy as np
import pandas as pd
import multiprocessing
# import awswrangler as wr
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Union, Any
from .sandbox import PythonSandbox
from ..parser.parsing    import clear_varname, clear_varname_dict
from ..files.files     import FileReader
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
    # This will be replaced with direct function call
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
        for funcname in ["read_pandas_dataFrame_from_s3"]:
            if not (python_code[i:].startswith(funcname)):
                continue
            if not (python_code[i + len(funcname):].strip().startswith("(")):
                continue
            func_call = python_code[i:].split(")")[0] + ")"
            if not (func_call in python_code):
                continue
            readfuncs.append(func_call)
    for readfunc in readfuncs:
        python_code = python_code.replace(readfunc, f"read_pandas_dataFrame_from_s3('{target_file}', 'csv')")

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

    # Add data loading call for the original dataframe
    prefix += f"\ndf_original = read_pandas_dataFrame_from_s3('{target_file}', 'csv')\n"

    for fromline in SAFE_FROM_MODULES:
        prefix = prefix.strip() + f"\n{fromline.strip()}\n"

    return (prefix.strip() + "\n" + python_code.strip() + "\n")

def _worker_exec(code: str, result_queue: multiprocessing.Queue):
    session_globals = {
        '__builtins__': SAFE_BUILTINS,
        'read_pandas_dataFrame_from_s3': read_pandas_dataFrame_from_s3,
        'pd': pd,
        'np': np,
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
            "stdout" : str(stdout.getvalue()).strip(),
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
    logger.info(f"=== EXECUTE_PYTHON_CODE START ===")
    logger.info(f"Data source file: {data_source_file}")
    logger.info(f"Raw Python code input:\n{python_code}")
    
    split_codes = PythonSandbox(content = python_code).split()
    logger.info(f"PythonSandbox split into {len(split_codes)} code blocks")
    
    for i, code in enumerate(split_codes):
        logger.info(f"=== PROCESSING CODE BLOCK {i+1}/{len(split_codes)} ===")
        logger.info(f"Original code block {i+1}:\n{code}")
        
        cleaned_code = _clean_python_code(code, data_source_file)
        logger.info(f"=== CLEANED CODE BLOCK {i+1} ===")
        logger.info(f"Cleaned code to execute:\n{cleaned_code}")
        
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target = _worker_exec,
            args   = (cleaned_code, result_queue)
        )
        process.start()
        process.join(timeout = TIMEOUT_SECONDS)
        response = {}
        
        logger.info(f"=== EXECUTION RESULT FOR BLOCK {i+1} ===")
        
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
            logger.error(f"Block {i+1}: TIMEOUT after {TIMEOUT_SECONDS}s")
            
        elif process.exitcode == 0:
            if not result_queue.empty():
                result = result_queue.get()
                result["execution_time"] = f"{time.time() - start_time:.3f}s"
                response = result
                logger.info(f"Block {i+1}: SUCCESS")
                logger.info(f"Block {i+1} stdout: {result.get('stdout', 'No output')}")
                if result.get('stderr'):
                    logger.warning(f"Block {i+1} stderr: {result['stderr']}")
            else:
                response = {
                    "success": False,
                    "stdout" : None,
                    "stderr" : None,
                    "error"  : "No result was returned from the execution process.",
                    "execution_time": f"{time.time() - start_time:.3f}s"
                }
                logger.error(f"Block {i+1}: No result returned from process")
        else:
            response = {
                "success": False,
                "stdout" : None,
                "stderr" : None,
                "error"  : f"Execution process crashed (exit code: {process.exitcode}).",
                "execution_time": f"{time.time() - start_time:.3f}s"
            }
            logger.error(f"Block {i+1}: CRASHED with exit code {process.exitcode}")
            
        # _debug_savecode(response, cleaned_code)
        
        if response["success"]:
            logger.info(f"=== EXECUTION COMPLETED SUCCESSFULLY WITH BLOCK {i+1} ===")
            break
        else:
            logger.warning(f"Block {i+1} failed, trying next block...")
            
    logger.info(f"=== EXECUTE_PYTHON_CODE END ===")
    logger.info(f"Final response: {response}")
    return (response)

def read_file_from_s3(
    s3_path: str,
    file_type: str
) -> pd.DataFrame:
    """
    Read file from S3 using AWS Data Wrangler.
    
    Args:
        s3_path: S3 path to the file (e.g., 's3://bucket/path/file.csv')
        file_type: Type of file to read ('csv', 'xlsx', 'parquet')
        
    Returns:
        Dict with status, result (DataFrame), error, and execution_time
    """
    start_time = time.perf_counter()
    try:
        fp = FileReader(s3_path, file_type)
        logger.info(f"INFO: Reading from path: { s3_path }")
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


def read_pandas_dataFrame_from_s3(s3_path: str, file_type: str):
    response = read_file_from_s3(s3_path, file_type)
    if (not response["status"]) or response["error"]:
        return (None)
    return response["result"]



