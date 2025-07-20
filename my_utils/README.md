# My Utils - Reusable Python Utilities

A collection of reusable utility functions with shared logging support.

## 🚀 Quick Setup

### 1. Install in Editable Mode
```bash
cd my_utils
pip install -e .
```

### 2. Use in Your Projects
```python
from my_utils import setup_logger, read_json_file, write_json_file

# Setup logger once in your main app
logger = setup_logger("my_app", log_file="app.log")

# All utils will use the same logger automatically
data = read_json_file("config.json")
write_json_file("output.json", data)
```

## 📦 Package Structure
```
my_utils/
├── setup.py              # Package configuration
├── my_utils/
│   ├── __init__.py       # Package exports
│   ├── setup_logger.py   # Logger setup & shared logger
│   ├── read_write.py     # File operations
│   ├── timer.py          # Performance timing
│   ├── safe_update_dict.py # Safe dictionary updates
│   ├── timezones_convertor.py # Timezone conversion
│   └── caller_info.py    # Function call tracking
```

## 🔧 Key Features

### Shared Logging
- **One logger** configured in main app
- **All utils** use the same logger instance
- **Single log file** for entire application

### Available Functions
- `setup_logger()` - Create application logger
- `get_app_logger()` - Get shared logger instance
- `read_json_file()` / `write_json_file()` - JSON operations
- `safe_update_dict()` - Safe dictionary updates
- `convert_iso_timestamp_to_timezone()` - Timezone conversion
- `measure_time` - Performance timing decorator

## 🎯 Usage Examples

### Basic Setup
```python
from my_utils import setup_logger

# Setup once in your main app
logger = setup_logger("my_app", log_file="app.log")
```

### File Operations
```python
from my_utils import read_json_file, write_json_file

# Read config
config = read_json_file("config.json")

# Write data
success = write_json_file("data.json", {"key": "value"})
```

### Dictionary Updates
```python
from my_utils import safe_update_dict

original = {"a": 1, "b": 2}
update = {"b": 3, "c": 4}
result = safe_update_dict(original, update)
```

### Performance Timing
```python
from my_utils import measure_time

@measure_time
def my_function():
    # Your code here
    pass
```

## 🔄 Git Installation

### From Local Repository
```bash
# Clone or navigate to your utils repo
cd my_utils

# Install in editable mode
pip install -e .
```

### From Remote Repository
```bash
# Install directly from git
pip install -e git+https://github.com/username/my_utils.git#egg=my_utils
```

## 📋 Requirements
- Python >= 3.8
- pytz >= 2021.1

## 🧪 Testing
```bash
cd my_utils
python test_logger.py
```

## 📝 Notes
- **Editable mode** (`-e`) allows code changes without reinstallation
- **Shared logger** ensures all utils log to the same file
- **Lazy loading** prevents import-time logger creation
- **Minimal dependencies** - only pytz required 