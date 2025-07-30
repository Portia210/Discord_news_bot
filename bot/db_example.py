#!/usr/bin/env python3
"""
Minimal CRUD examples using generic CRUD class.
"""

#%%
# Setup: Initialize database and create CRUD instance
from db.init_db import init_db
from db.engine import get_db_sync
from db.crud import CRUDBase
from db.models import SymbolsList

# Initialize database
init_db()

# Create CRUD instance
symbols_crud = CRUDBase(SymbolsList)
db = get_db_sync()

#%%
# Example 1: CREATE - Add a new symbol
print("=== Example 1: CREATE ===")
symbol_data = {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "exchange": "NASDAQ",
    "type": "Stock"
}

new_symbol = symbols_crud.create(db, symbol_data)
print(f"Created: {new_symbol.symbol} - {new_symbol.name}")

#%%
# Example 2: READ - Get symbol by field
print("=== Example 2: READ ===")
symbol = symbols_crud.get_by_field(db, "symbol", "AAPL")
if symbol:
    # print all fields of symbol
    for field, value in symbol.__dict__.items():
        print(f"{field}: {value}")

#%%
# Example 3: UPDATE - Modify existing symbol
print("=== Example 3: UPDATE ===")
update_data = {"name": "Apple Inc. (Updated)"}
updated_symbol = symbols_crud.update_by_field(db, "symbol", "AAPL", update_data)
if updated_symbol:
    print(f"Updated: {updated_symbol.symbol} - {updated_symbol.name}")

db.close()
print("=== Examples completed ===") 
# %%
db.close()
# %%
