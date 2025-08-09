import requests
from config import Config
from db.init_db import init_db
from db.engine import get_db_sync
from db.crud import CRUDBase
from db.models import SymbolsList
from scrapers import get_symbols_list


def populate_symbols_database():
    """Populate the SymbolsList table with data from the API using bulk operations."""
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        
        # Get database session
        db = get_db_sync()
        
        # Get symbols from API
        print("Fetching symbols from API...")
        symbols_data = get_symbols_list()
        
        if not symbols_data:
            print("Failed to get symbols data from API")
            return False
        
        print(f"Found {len(symbols_data)} symbols to process")
        
        # Get existing symbols to avoid duplicates
        existing_symbols = {s.symbol for s in db.query(SymbolsList.symbol).all()}
        print(f"Database already contains {len(existing_symbols)} symbols")
        
        # Prepare bulk data
        symbols_to_add = []
        skipped_count = 0
        
        for item in symbols_data:
            if item["symbol"] in existing_symbols:
                skipped_count += 1
                continue
                
            # Prepare data for database
            symbol_data = {
                "symbol": item["symbol"],
                "name": item["name"],
                "exchange": item.get("exchangeShortName", None),
                "type": item.get("type", None),
            }
            
            symbols_to_add.append(SymbolsList(**symbol_data))
        
        print(f"Prepared {len(symbols_to_add)} symbols for bulk insert")
        print(f"Skipped {skipped_count} existing symbols")
        
        # Bulk insert
        if symbols_to_add:
            print("Performing bulk insert...")
            db.bulk_save_objects(symbols_to_add)
            db.commit()
            print(f"Bulk insert completed! Added {len(symbols_to_add)} symbols")
        else:
            print("No new symbols to add")
        
        db.close()
        
        return True
        
    except Exception as e:
        print(f"Error populating database: {e}")
        return False


def main():
    from datetime import datetime
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()

