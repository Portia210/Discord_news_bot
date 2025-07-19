import json
import pandas as pd

# Load the table paths configuration
with open('table_pathes.json', 'r') as f:
    table_pathes = json.load(f)

# Read the events data
with open('events_data_Monday, May 26, 2025.json', 'r') as f:
    events_data = json.load(f)

# Get columns from table_pathes
columns = list(table_pathes.keys())

# Create DataFrame with explicit dtype for each column
df = pd.DataFrame(events_data, columns=columns)



