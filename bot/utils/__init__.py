"""
Utils Package - Centralized access to all utility functions
"""

# Logger
from .logger import logger, setup_logger

# File Operations
from .read_write import (
    read_text_file,
    write_text_file,
    read_json_file,
    write_json_file,
    write_binary_file
)

# Time and Date Utilities
from .timezones_convertor import convert_iso_time_to_datetime, get_time_deltas_for_date_range, get_time_delta_for_date
from .timer import measure_time
from .parse_hebrew_date import parse_hebrew_date

# Data Processing
from .safe_update_dict import safe_update_dict
from .caller_info import get_function_and_caller_info

# HTML/PDF Conversion
from .html_convertor import html_to_pdf, convert_html_to_image

from .get_json_tree import get_json_tree

# Main functions and classes to expose
__all__ = [
    # Logger
    'logger',
    'setup_logger',
    
    # File Operations
    'read_text_file',
    'write_text_file',
    'read_json_file',
    'write_json_file',
    'write_binary_file',
    
    # Time and Date
    'convert_iso_time_to_datetime',
    'get_time_deltas_for_date_range',
    'get_time_delta_for_date',
    'measure_time',
    'parse_hebrew_date',
    
    # Data Processing
    'safe_update_dict',
    'get_function_and_caller_info',
    
    # HTML/PDF
    'html_to_pdf',
    'convert_html_to_image',
    
    # JSON Tree
    'get_json_tree',
]


