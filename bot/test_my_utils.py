#!/usr/bin/env python3
"""
Test file for my_utils functions in the bot directory
"""

import os
import sys
from datetime import datetime
import pytz


from my_utils import (
    setup_logger, 
    get_app_logger,
    read_json_file, 
    write_json_file, 
    safe_update_dict,
    convert_iso_timestamp_to_timezone,
    measure_time
)


setup_logger(
    name="test_app",
    level=10,  # DEBUG
    log_file="test.log"
)

@measure_time
def main():
    print("hello")


main()