from typing import Optional, Union, Literal


def get_json_tree(data_structure, path_format: Literal["json", "python"] = "python", **kwargs):
    """
    Get the structure of a JSON object, organized like a tree with proper indentation.
    show only the first value for lists.
    the output could be saved as a yaml file for easy reading and code colapsing.

    Args:
        data_structure: the json object to get the structure of
        path_format: format for paths ("json" or "python")
        **kwargs: additional parameters (indent_level, path)

    Returns:
        a string with the structure of the json object
    """

    
    # Extract kwargs with defaults
    indent_level = kwargs.get("indent_level", 0)
    path = kwargs.get("path", "")
    
    output = ""
    indent_str = "  " * indent_level  # 2 spaces per indent level

    if isinstance(data_structure, dict):
        if not data_structure:  # Empty dict
            output += f"_DICT_ (level {indent_level}), path: {path} (empty)\n"
        else:
            output += f"_DICT_ (level {indent_level}), path: {path}\n"

            # Separate simple and complex keys
            complex_keys = {key: value for key, value in data_structure.items() if isinstance(value, (list, dict))}
            simple_keys = {key: value for key, value in data_structure.items() if not isinstance(value, (list, dict))}
            
            # Show simple keys on the same line
            for key, value in simple_keys.items():
                output += f"{indent_str}  {key}: {get_json_tree(value, path_format=path_format, indent_level=indent_level + 1, path=path)}\n"
            
            # Show complex keys with proper indentation
            for key, value in complex_keys.items():
                if path_format == "json":
                    new_path = f"{path}.{key}" 
                elif path_format == "python":
                    new_path = f"{path}[\"{key}\"]" 
                else:
                    raise ValueError(f"Invalid path format: {path_format}")
                
                output += f"{indent_str}  {key}: {get_json_tree(value, path_format=path_format, indent_level=indent_level + 1, path=new_path)}\n"
            output = output.rstrip()  # Remove trailing newline
    elif isinstance(data_structure, list):
        if not data_structure:  # Empty list
            output += f"_LIST_ (level {indent_level}), path: {path} (empty)\n"
        else:
            output += f"_LIST_ (level {indent_level}), path: {path}\n"
            # Only process the first item in the list
            new_path = f"{path}[0]" if path else "[0]"
            output += f"{indent_str}  {get_json_tree(data_structure[0], path_format=path_format, indent_level=indent_level + 1, path=new_path)}\n"
            output = output.rstrip()  # Remove trailing newline
    else:
        if isinstance(data_structure, str):
            output += f"_STR_ = {data_structure[:50]}" + ("..." if len(data_structure) > 50 else "")
        else:
            output += f"_{type(data_structure).__name__.upper()}_ = {data_structure}"
        output = output.rstrip()  # Remove trailing newline
    
    return output

        
        
        
if __name__ == "__main__":
    from utils import read_json_file
    json_input = read_json_file("data/yf/example.json")
    output = get_json_tree({"a": {"b": "c", "x": {"y": None}}, "c": "d"}, path_format="python")
    print(output)
    with open("data/yf/example.yaml", "w") as f:
        f.write(output)
        
    print(json_input["secFilings"]["filings"][0]["exhibits"][0])

