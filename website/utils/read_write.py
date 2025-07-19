import json
from utils.logger import logger
from utils.caller_info import get_function_and_caller_info

def read_text_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path} ({get_function_and_caller_info()})")
        return None
    except Exception as e:
        logger.error(f"Error in read_text_file: {str(e)} ({get_function_and_caller_info()})")
        return None

def write_text_file(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)
        logger.debug(f"File written to {file_path}")
    except Exception as e:
        logger.error(f"Error in write_text_file: {str(e)} ({get_function_and_caller_info()})")
        return None

def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path} ({get_function_and_caller_info()})")
        return None
    except json.JSONDecodeError:
        logger.error(f"JSONDecodeError in read_json_file: {file_path} ({get_function_and_caller_info()})")
        return None
    except Exception as e:
        logger.error(f"Error in read_json_file: {str(e)} ({get_function_and_caller_info()})")
        return None

def write_json_file(file_path, data, indent=4):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except json.JSONDecodeError:
        logger.error(f"JSONDecodeError in write_json_file: {file_path} ({get_function_and_caller_info()})")
        return None
    except Exception as e:
        logger.error(f"Error in write_json_file: {str(e)} ({get_function_and_caller_info()})")
        return None

def write_binary_file(file_path, data):
    try:
        with open(file_path, "wb") as f:
            f.write(data)
    except Exception as e:
        logger.error(f"Error in write_binary_file: {str(e)} ({get_function_and_caller_info()})")
        return None


