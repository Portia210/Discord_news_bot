import re


def safe_get(data_structure, path):
    """
    Safely access nested dict/list values using a Python-style path string.
    Example path: ["quoteSummary"]["result"][0]["price"]["longName"]
    
    Args:
        d: The dictionary/list to search in
        path: Python-style path string starting with brackets
        default: Default value to return if path not found
    
    Returns:
        The value at the path or default if not found
    """
    if not path or data_structure is None:
        return None
    
    # Remove leading/trailing whitespace
    path = path.strip()
    
    # Find all keys/indices: ["key"] or [0]
    tokens = re.findall(r'\["([^"]+)"\]|\[(\d+)\]', path)
    current = data_structure
    for key, idx in tokens:
        try:
            if key:  # dict access: ["key"]
                if isinstance(current, dict):
                    current = current.get(key)
                else:
                    return None
            elif idx:  # list access: [0]
                if isinstance(current, list):
                    current = current[int(idx)]
                else:
                    return None
        except (KeyError, IndexError, TypeError, AttributeError):
            return None
        
        if current is None:  # stop early if value is None
            return None
    
    return current