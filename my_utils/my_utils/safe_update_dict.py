from utils.logger import logger
from utils.caller_info import get_function_and_caller_info

def safe_update_dict(original_dict, update_dict, prevent_type_mismatch: bool = True):
    """
    Update a dictionary safely, ensuring that only existing keys are updated.
    Handles nested dictionaries recursively.
    
    Args:
        original_dict (dict): The original dictionary to update.
        update_dict (dict): The dictionary to update the original dictionary with.

    Returns:
        dict: The updated dictionary.
    """
    for key, value in update_dict.items():
        if key in original_dict:
            # If both values are dictionaries, recursively update
            if isinstance(value, dict) and isinstance(original_dict[key], dict):
                safe_update_dict(original_dict[key], value)
            # if they are not the same type (any type), don't update
            elif prevent_type_mismatch and type(value) is not type(original_dict[key]):
                logger.warning(f"Preventing update for key {key} because types are different: original: {type(original_dict[key])} VS update: {type(value)} ({get_function_and_caller_info()})")
            else:
                original_dict[key] = value
        else:
            logger.warning(f"Key {key} not found in original dictionary, ignoring it ({get_function_and_caller_info()})")
    return original_dict


if __name__ == "__main__":
    dict1 = {"a": 1, "b": "2", "c": {"d": {"x": 1, "y": 2}, "e": 4}}
    dict2 = {"b": 20, "c": {"d": 30, "f": 5}}

    safe_update_dict(dict1, dict2)
    print(dict1)


