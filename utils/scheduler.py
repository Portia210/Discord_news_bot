import asyncio
from datetime import datetime, time, timedelta
from utils.logger import logger
from discord_utils.message_handler import get_message_handler
from config import config

class TaskScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduled_tasks = {}
        self.running = False
    
    async def schedule_daily_export(self, channel_id: int, hour: int = 14, minute: int = 0):
        """
        Schedule daily message export at a specific time
        
        Args:
            channel_id (int): Discord channel ID to export
            hour (int): Hour (24-hour format, default: 14 for 2 PM)
            minute (int): Minute (default: 0)
        """
        task_name = f"daily_export_{channel_id}"
        
        if task_name in self.scheduled_tasks:
            logger.info(f"Task {task_name} already scheduled")
            return
        
        async def daily_export_task():
            while self.running:
                try:
                    now = datetime.now(config.app_timezone)
                    target_time = time(hour, minute)
                    
                    # Calculate next run time
                    if now.time() >= target_time:
                        # If it's past the target time today, schedule for tomorrow
                        next_run = datetime.combine(now.date() + timedelta(days=1), target_time)
                    else:
                        # Schedule for today
                        next_run = datetime.combine(now.date(), target_time)
                    
                    # Calculate seconds to wait
                    wait_seconds = (next_run - now).total_seconds()
                    logger.info(f"Next export scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in {wait_seconds:.0f} seconds)")
                    
                    # Wait until next run time
                    await asyncio.sleep(wait_seconds)
                    
                    # Perform the export
                    if self.running:
                        logger.info(f"Starting scheduled export for channel {channel_id}")
                        message_handler = get_message_handler(self.bot)
                        filepath = await message_handler.export_channel_to_text(channel_id, hours_back=24)
                        
                        if filepath:
                            logger.info(f"Scheduled export completed: {filepath}")
                        else:
                            logger.error("Scheduled export failed")
                    
                except Exception as e:
                    logger.error(f"Error in scheduled export task: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
        
        # Start the task
        self.scheduled_tasks[task_name] = asyncio.create_task(daily_export_task())
        logger.info(f"Scheduled daily export for channel {channel_id} at {hour:02d}:{minute:02d}")
    
    def start(self):
        """Start the scheduler"""
        self.running = True
        logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the scheduler and cancel all tasks"""
        self.running = False
        for task_name, task in self.scheduled_tasks.items():
            task.cancel()
            logger.info(f"Cancelled task: {task_name}")
        self.scheduled_tasks.clear()
        logger.info("Task scheduler stopped")

# Global scheduler instance
scheduler = None

def get_scheduler(bot):
    """Get or create the global scheduler instance"""
    global scheduler
    if scheduler is None:
        scheduler = TaskScheduler(bot)
    return scheduler 