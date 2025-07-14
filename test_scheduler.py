#!/usr/bin/env python3
"""
Test script to verify scheduler imports and basic functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all scheduler imports"""
    try:
        print("🔍 Testing scheduler imports...")
        
        # Test core imports
        from scheduler import Scheduler, CalendarManager
        print("✅ Core scheduler imports successful")
        
        # Test custom tasks
        from scheduler.custom_tasks import CustomTasks
        print("✅ Custom tasks import successful")
        
        # Test task definitions
        from scheduler.task_definitions import TaskDefinitions
        print("✅ Task definitions import successful")
        
        # Test individual modules
        from scheduler.tasks import Task, TaskCondition, parse_days
        print("✅ Tasks module import successful")
        
        print("\n🎉 All imports successful! Scheduler is ready to use.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_task_creation():
    """Test creating a simple task"""
    try:
        print("\n🔍 Testing task creation...")
        
        from scheduler.tasks import Task, parse_days
        
        # Create a simple test task
        async def test_func():
            print("✅ Test task executed successfully!")
        
        task = Task(
            name="test_task",
            func=test_func,
            time_str="12:00",
            days=parse_days("mon-fri")
        )
        
        print("✅ Task creation successful")
        print(f"   Task name: {task.name}")
        print(f"   Schedule time: {task.time_str}")
        print(f"   Days: {task.days}")
        
        return True
        
    except Exception as e:
        print(f"❌ Task creation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Scheduler Test Suite")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test task creation
        task_ok = test_task_creation()
        
        if task_ok:
            print("\n🎉 All tests passed! Your scheduler is ready to use.")
            print("\nNext steps:")
            print("1. Run your bot: python bot.py")
            print("2. Check the logs for scheduler initialization")
            print("3. Monitor your Discord channel for alerts")
        else:
            print("\n❌ Task creation test failed")
            sys.exit(1)
    else:
        print("\n❌ Import test failed")
        sys.exit(1) 