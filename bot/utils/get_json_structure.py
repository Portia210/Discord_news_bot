from typing import Optional, Union, Literal


def get_json_tree(data_structure: Union[dict, list, str, int, float, None] = None, indent_level: int = 0, path: str = "", path_format: Optional[Literal["json", "python"]] = "python"):
    """
    Get the structure of a JSON object, organized like a tree with proper indentation.
    Shows only types, not values. For lists, only shows the first object.
    Includes JSON path for each dict and list.
    """
    if data_structure is None:
        return "None"
    
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
                output += f"{indent_str}  {key}: {get_json_tree(value, indent_level + 1, '', path_format)}\n"
            
            # Show complex keys with proper indentation
            for key, value in complex_keys.items():
                if path_format == "json":
                    new_path = f"{path}.{key}" 
                elif path_format == "python":
                    new_path = f"{path}[\"{key}\"]" 
                else:
                    raise ValueError(f"Invalid path format: {path_format}")
                
                output += f"{indent_str}  {key}: {get_json_tree(value, indent_level + 1, new_path, path_format)}\n"
            output = output.rstrip()  # Remove trailing newline
    elif isinstance(data_structure, list):
        if not data_structure:  # Empty list
            output += f"_LIST_ (level {indent_level}), path: {path} (empty)\n"
        else:
            output += f"_LIST_ (level {indent_level}), path: {path}\n"
            # Only process the first item in the list
            new_path = f"{path}[0]" if path else "[0]"
            output += f"{indent_str}  {get_json_tree(data_structure[0], indent_level + 1, new_path, path_format)}\n"
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
    with open("data/yf/example.yaml", "w") as f:
        output = get_json_tree(json_input, path_format="python")
        f.write(output)
        
    print(json_input["secFilings"]["filings"][0]["exhibits"][0])

