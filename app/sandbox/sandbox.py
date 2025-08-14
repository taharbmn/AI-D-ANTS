import io
import uuid
import pandas
import contextlib
import multiprocessing
from app.extractors.python_extractor import PythonExtractor

SAFE_BUILTINS = {
    # '__builtins__': __builtins__,
    'print'       : print,
    'type'        : type,
    'all'         : all,
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

def _worker_exec(code: str, result_queue: multiprocessing.Queue, builtins, retvar_name: str = ""):
    stdout = io.StringIO()
    stderr = io.StringIO()
    session_globals = {
        '__builtins__': builtins,
        "pd"          : pandas,
        "pandas"      : pandas
    }
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exec(code, session_globals)
        result_queue.put(
            {
                "success"  : True,
                "status"   : 200,
                "stdout"   : str(stdout.getvalue()).strip(),
                "stderr"   : str(stderr.getvalue()).strip(),
                "return"   : session_globals.get(retvar_name),
                "error"    : None
            }
        )
    except Exception as e:
        result_queue.put(
            {
                "success"  : False,
                "status"   : 500,
                "stdout"   : str(stdout.getvalue()).strip(),
                "stderr"   : str(stderr.getvalue()).strip(),
                "return"   : session_globals.get(retvar_name),
                "error"    : f"{type(e).__name__}: {str(e)}\n{stderr.getvalue()}",
            }
        )

class PythonSandbox:

    def __init__(self, code):
        self._code = code

    def get_function_by_name(self, name: str):
        for function in PythonExtractor(self._code).functions:
            if function["name"] == name:
                return function
        return None

    def map_arguments(self, args):
        if not args:
            args = []
        builtins = SAFE_BUILTINS.copy()
        argnames = []
        for argument in args:
            argname = ("a" + str(uuid.uuid4())).replace("-","")
            while (argname in builtins):
                argname = ("a" + str(uuid.uuid4())).replace("-","")
            argnames.append(argname)
            builtins[argname] = argument
        return [argnames, builtins]

    def _get_new_varname(self, argnames, function_body, builtins):
        retvar_name = ("a" + str(uuid.uuid4())).replace("-","")
        while (retvar_name in builtins) or (retvar_name in argnames) or (retvar_name in function_body):
            retvar_name = ("a" + str(uuid.uuid4())).replace("-","")
        return retvar_name

    def call_function(self, name, args, timeout: int, kwargs: dict = None):
        """
            Calls a function by name with the provided arguments in a sandboxed environment.
            Args:
                name (str): The name of the function to call.
                args (list): The arguments to pass to the function.
                kwargs (dict, optional): Keyword arguments to pass to the function.
                timeout (int): Timeout in seconds for the execution.
            return:
                {
                    "success"  : bool,
                    "status"   : 200 | 500,
                    "stdout"   : str,
                    "stderr"   : str,
                    "return"   : any,
                    "error"    : str | None
                }
        """
        function = self.get_function_by_name(name)
        if not function:
            raise ValueError(f"Function '{name}' not found in the provided code.")
        function_body = function['body']
        if not isinstance(function_body, str) or not function_body.strip():
            raise ValueError(f"Function '{name}' has no valid body.")
        [argnames, builtins] = self.map_arguments(args)
        retvar_name = self._get_new_varname(argnames, function_body, builtins)
        code = function['body'].rstrip() + "\n" + retvar_name + "=" + function['name'] + "("
        if argnames:
            for argname in argnames:
                code += argname + ", "
            code = code.strip(" ,")
        code += ")"
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target = _worker_exec,
            args   = (code, result_queue, builtins, retvar_name)
        )
        process.start()
        process.join(timeout = timeout)
        if process.is_alive():
            process.terminate()
            process.join()
            return {
                "success"  : False,
                "status"   : 500,
                "stdout"   : "",
                "stderr"   : "",
                "return"   : None,
                "error"    : f"TimeoutError: Execution timed out after {timeout} seconds."
            }
        elif process.exitcode == 0:
            if result_queue.empty():
                return {
                    "success"  : False,
                    "status"   : 500,
                    "stdout"   : "",
                    "stderr"   : "",
                    "return"   : None,
                    "error"    : "No result was returned from the execution process."
                }
            result = result_queue.get()
            return result
        return {
            "success"  : False,
            "status"   : 500,
            "stdout"   : "",
            "stderr"   : "",
            "return"   : None,
            "error"    : f"Process exited with code {process.exitcode}."
        }