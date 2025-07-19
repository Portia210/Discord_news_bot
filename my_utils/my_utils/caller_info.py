import inspect

def get_function_and_caller_info():
    """Get information about the calling function"""
    try:
        # Get the stack trace
        stack = inspect.stack()
        # The caller is at index 2 (0=current function, 1=this function, 2=caller)
        if len(stack) >= 3:
            caller_frame = stack[2]
            # Get the function name from the previous frame (the actual function being called)
            function_frame = stack[1]
            function_name = function_frame.function
            # Get full path and line number
            full_path = caller_frame.filename
            line_number = caller_frame.lineno
            return f"{function_name} function called at {full_path}:{line_number}"
        else:
            return "unknown"
    except Exception:
        return "unknown" 