#!/usr/bin/env python3
"""
Test Individual Tasks - Test each task function independently
"""

import sys
import os
import asyncio


# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_specific_task(task_name: str):
    """Test a specific task by name"""
    print(f"\n🔍 Testing Specific Task: {task_name}")
    print("=" * 40)
    
    try:
        # Import all task modules
        from scheduler_v2.tasks.daily_tasks import (
            daily_report_task,
            daily_schedule_task,
            evening_summary_task,
            system_health_check_task
        )
        
        # Get the task function
        task_func = globals().get(task_name)
        
        if task_func and callable(task_func):
            print(f"✅ Found task: {task_name}")
            await task_func()
            print(f"✅ Task {task_name} executed successfully!")
            return True
        else:
            print(f"❌ Task {task_name} not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing task {task_name}: {e}")
        return False


async def main():
    """Main test function"""
    print("🚀 Individual Task Test Suite")
    print("=" * 50)
    
    # Test specific task
    task_name = "daily_report_task"
    success = await test_specific_task(task_name)
  
    if success:
        print("✅ Task executed successfully!")
    else:
        print("❌ Task execution failed")


if __name__ == "__main__":
    asyncio.run(main()) 