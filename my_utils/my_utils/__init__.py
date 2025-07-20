"""
My Utils - A collection of reusable utility functions
"""

from .safe_update_dict import safe_update_dict
from .setup_logger import setup_logger, get_app_logger
from .timer import measure_time
from .timezones_convertor import convert_iso_timestamp_to_timezone
from .read_write import read_text_file, write_text_file, read_json_file, write_json_file, write_binary_file
from .caller_info import get_function_and_caller_info

__version__ = "1.0.0"
__author__ = "Portia210"

__all__ = [
    "setup_logger",
    "get_app_logger",
    "measure_time",
    "convert_iso_timestamp_to_timezone",
    "read_text_file",
    "write_text_file", 
    "read_json_file",
    "write_json_file",
    "write_binary_file",
    "safe_update_dict",
    "get_function_and_caller_info",
] 