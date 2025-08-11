def clear_varname(varname: str):
    """
    Clear a variable name by converting it to lowercase and removing
    any non-alphanumeric characters.
    """
    varname = str(varname).lower()
    for c in list(varname):
        if not c.isalnum():
            varname = varname.replace(c, '')
    return varname

def clear_varname_dict(data):
    """
    Normalize the input data by stripping whitespace, removing underscores,
    and converting keys to lowercase.
    """
    if not isinstance(data, dict):
        raise ValueError("Input data must be a dictionary")
    _data = {}
    for key, val in data.items():
        key = clear_varname(key)
        _data[key] = val
    return (_data)