"""
Core Scheduler - Main scheduler class
"""

import asyncio
import pytz
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
from utils.logger import logger
from config import Config
from scheduler.tasks import Task


class Scheduler:
    """Main scheduler class for managing tasks"""
    
    def __init__(self, timezone: pytz.timezone = None):
        self.timezone = timezone or pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
        self.tasks: Dict[str, Task] = {}
        self.running = False
        self.task_handles: Dict[str, asyncio.Task] = {}
    
    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler"""
        self.tasks[task.name] = task
        logger.info(f"📅 Added task: {task.name}")
    
    def remove_task(self, name: str) -> None:
        """Remove a task from the scheduler"""
        if name in self.tasks:
            if name in self.task_handles:
                self.task_handles[name].cancel()
                del self.task_handles[name]
            del self.tasks[name]
            logger.info(f"🗑️ Removed task: {name}")
    
    async def _run_task_loop(self, task: Task):
        """Main loop for a single task"""
        while self.running:
            try:
                # Calculate next run time
                next_run = task.get_next_run()
                wait_seconds = (next_run - datetime.now(self.timezone)).total_seconds()
                
                if wait_seconds > 0:
                    logger.info(f"⏰ Task '{task.name}' scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                    await asyncio.sleep(wait_seconds)
                
                if not self.running:
                    break
                
                # Check conditions before executing
                if await task.check_conditions():
                    logger.info(f"🛑 Task '{task.name}' cancelled due to conditions")
                    break
                
                # Execute task
                await task.execute()
                
                # Wait before next iteration
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Error in task loop '{task.name}': {e}")
                await asyncio.sleep(300)
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("⚠️ Scheduler is already running")
            return
        
        self.running = True
        logger.info("🚀 Starting Scheduler")
        
        # Start all tasks
        for task in self.tasks.values():
            self.task_handles[task.name] = asyncio.create_task(self._run_task_loop(task))
        
        logger.info(f"📅 Started {len(self.tasks)} tasks")
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.running = False
        logger.info("🛑 Stopping Scheduler")
        
        # Cancel all task handles
        for name, handle in self.task_handles.items():
            handle.cancel()
            logger.info(f"🛑 Cancelled task: {name}")
        
        self.task_handles.clear()
        logger.info("✅ Scheduler stopped")
    
    def get_status(self) -> Dict:
        """Get status of all tasks"""
        status = {}
        for name, task in self.tasks.items():
            status[name] = {
                'next_run': task.get_next_run().strftime('%Y-%m-%d %H:%M:%S'),
                'is_running': task.is_running,
                'days': task.days,
                'time': task.time_str,
                'conditions': len(task.conditions)
            }
        return status 