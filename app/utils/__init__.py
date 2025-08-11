import os

def get_local_data_dir() -> str:
    """
    Returns the path to the local data directory.
    """
    basename = "local-data"
    if os.environ.get("LOCAL_DATA_DIR"):
        return os.environ["LOCAL_DATA_DIR"]
    dirname = os.path.dirname(os.path.abspath(__file__))
    while dirname and dirname != os.path.dirname(dirname):
        if os.path.exists(os.path.join(dirname, basename)):
            if os.path.isdir(os.path.join(dirname, basename)):
                os.environ["LOCAL_DATA_DIR"] = os.path.join(dirname, basename)
                return os.environ["LOCAL_DATA_DIR"]
        dirname = os.path.dirname(dirname)
    raise FileNotFoundError(
        f"Local data directory not found. Please set the LOCAL_DATA_DIR environment variable or create a '{basename}' directory in the project root."
    )
    return None

def get_system_prompt_dir() -> str:
    path = os.path.dirname(os.path.abspath(__file__))
    while path and path != os.path.dirname(path):
        sysdir = os.path.join(path, "app", "system_prompt")
        if os.path.exists(sysdir):
            return sysdir
        path = os.path.dirname(path)
    raise FileNotFoundError(
        "System prompt directory not found. Please ensure the 'system_prompt' directory exists in the app directory."
    )

def load_system_prompt(name: str) -> str:
    """
    Loads a system prompt from the local data directory.
    """
    sysdir = get_system_prompt_dir()
    name   = name.strip().lower()
    for basename in os.listdir(sysdir):
        if basename.strip().lower() == name:
            try:
                return open(os.path.join(sysdir, basename)).read()
            except:
                pass
        if basename.strip().lower() == name + ".md":
            try:
                return open(os.path.join(sysdir, basename)).read()
            except:
                pass
    raise FileNotFoundError(
        f"System prompt '{name}' not found in the system prompt directory."
    )