#!/usr/bin/env python3
"""
Force close all database connections.
Run this when you get "database is locked" errors.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add bot directory to path
sys.path.insert(0, str(Path(__file__).parent))

def force_close_database():
    """Force close all database connections and processes."""
    
    print("🔄 Force closing database connections...")
    
    try:
        # Method 1: Try to dispose engine
        from db.engine import engine
        engine.dispose()
        print("✅ Engine disposed")
    except Exception as e:
        print(f"⚠️ Engine dispose failed: {e}")
    
    # Method 2: Kill Python processes that might be holding the file
    try:
        print("🔄 Killing Python processes...")
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                      capture_output=True, text=True)
        print("✅ Python processes killed")
    except Exception as e:
        print(f"⚠️ Could not kill Python processes: {e}")
    
    # Method 3: Wait a moment for processes to fully close
    print("⏳ Waiting for processes to close...")
    time.sleep(2)
    
    # Method 4: Try to remove the database file
    db_file = "bot_data.db"
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✅ Removed database file: {db_file}")
            return True
        except Exception as e:
            print(f"❌ Could not remove file: {e}")
            
            # Method 5: Try to rename the file
            try:
                backup_name = f"{db_file}.locked.{int(time.time())}"
                os.rename(db_file, backup_name)
                print(f"✅ Renamed database file to: {backup_name}")
                return True
            except Exception as e2:
                print(f"❌ Could not rename file: {e2}")
    
    return False

if __name__ == "__main__":
    success = force_close_database()
    
    if success:
        print("🎉 Database successfully closed/removed!")
    else:
        print("❌ Could not fully close database. Try restarting your terminal/IDE.")
        print("💡 Alternative: Restart your computer if the issue persists.") 