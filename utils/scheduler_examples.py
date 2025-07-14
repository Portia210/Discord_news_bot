"""
Example usage of the Advanced Scheduler for Discord bot tasks
"""

import asyncio
from utils.advanced_scheduler import AdvancedScheduler, create_condition, parse_days
from utils.logger import logger
from yf_scraper.yf_requests import YfRequests
from news_pdf.pdf_report_generator import PdfReportGenerator
import discord


class BotScheduler:
    """Scheduler specifically for Discord bot tasks"""
    
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.scheduler = AdvancedScheduler()
        self.yf_requests = YfRequests()
        self.pdf_generator = PdfReportGenerator(bot)
    
    async def check_market_closed(self) -> bool:
        """Check if market is closed - cancel tasks if true"""
        try:
            market_data = self.yf_requests.get_market_time()
            market_status = market_data["finance"]["marketTimes"][0]["marketTime"][0]["status"]
            return market_status == "closed"
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return False
    
    async def check_holiday(self) -> bool:
        """Check if it's a holiday - cancel tasks if true"""
        # You can implement holiday checking logic here
        # For now, return False (not a holiday)
        return False
    
    async def daily_market_report(self):
        """Generate and send daily market report"""
        try:
            logger.info("📊 Generating daily market report...")
            success = await self.pdf_generator.generate_pdf_report(
                report_time='auto',
                hours_back=24
            )
            if success:
                logger.info("✅ Daily market report completed")
            else:
                logger.error("❌ Daily market report failed")
        except Exception as e:
            logger.error(f"❌ Error in daily market report: {e}")
    
    async def weekly_backup(self):
        """Weekly backup task"""
        try:
            logger.info("💾 Starting weekly backup...")
            # Add your backup logic here
            await asyncio.sleep(5)  # Simulate backup process
            logger.info("✅ Weekly backup completed")
        except Exception as e:
            logger.error(f"❌ Error in weekly backup: {e}")
    
    async def market_open_check(self):
        """Check market status when it opens"""
        try:
            logger.info("🔍 Checking market open status...")
            market_data = self.yf_requests.get_market_time()
            market_status = market_data["finance"]["marketTimes"][0]["marketTime"][0]["status"]
            logger.info(f"📈 Market status: {market_status}")
        except Exception as e:
            logger.error(f"❌ Error checking market status: {e}")
    
    def setup_tasks(self):
        """Setup all scheduled tasks"""
        
        # Daily market report at 2:30 PM (weekdays only)
        self.scheduler.add_task(
            name="daily_market_report",
            func=self.daily_market_report,
            time_str="14:30",
            days=parse_days("mon-fri"),
            conditions=[
                create_condition("market_closed", self.check_market_closed),
                create_condition("holiday", self.check_holiday)
            ]
        )
        
        # Market open check at 9:30 AM (weekdays only)
        self.scheduler.add_task(
            name="market_open_check",
            func=self.market_open_check,
            time_str="09:30",
            days=parse_days("mon-fri")
        )
        
        # Weekly backup on Sunday at 2:00 AM
        self.scheduler.add_task(
            name="weekly_backup",
            func=self.weekly_backup,
            time_str="02:00",
            days=["sun"]
        )
        
        # Morning report at 8:00 AM (weekdays)
        self.scheduler.add_task(
            name="morning_report",
            func=self.daily_market_report,
            time_str="08:00",
            days=parse_days("mon-fri"),
            conditions=[
                create_condition("market_closed", self.check_market_closed)
            ]
        )
        
        logger.info("📅 All tasks scheduled successfully")
    
    async def start(self):
        """Start the scheduler"""
        self.setup_tasks()
        await self.scheduler.start()
    
    async def stop(self):
        """Stop the scheduler"""
        await self.scheduler.stop()
    
    def get_status(self):
        """Get status of all tasks"""
        return self.scheduler.get_task_status()


# Example usage in your bot
async def setup_bot_scheduler(bot: discord.Client):
    """Setup scheduler for the bot"""
    scheduler = BotScheduler(bot)
    await scheduler.start()
    return scheduler


# Example Discord commands for scheduler management
class SchedulerCommands:
    def __init__(self, bot_scheduler: BotScheduler):
        self.scheduler = bot_scheduler
    
    async def status_command(self, ctx):
        """Discord command to show scheduler status"""
        status = self.scheduler.get_status()
        
        embed = discord.Embed(title="📅 Scheduler Status", color=0x00ff00)
        
        for task_name, task_info in status.items():
            status_text = f"**Next Run:** {task_info['next_run']}\n"
            status_text += f"**Days:** {', '.join(task_info['days'])}\n"
            status_text += f"**Time:** {task_info['time']}\n"
            status_text += f"**Conditions:** {task_info['conditions']}\n"
            status_text += f"**Running:** {'✅' if task_info['is_running'] else '❌'}"
            
            embed.add_field(name=task_name, value=status_text, inline=False)
        
        await ctx.send(embed=embed)
    
    async def add_task_command(self, ctx, name: str, time_str: str, days: str = "mon-fri"):
        """Discord command to add a new task"""
        try:
            # This is a simplified example - you'd need to implement the actual task function
            async def custom_task():
                await ctx.send(f"Custom task '{name}' executed!")
            
            self.scheduler.scheduler.add_task(
                name=name,
                func=custom_task,
                time_str=time_str,
                days=parse_days(days)
            )
            
            await ctx.send(f"✅ Task '{name}' added successfully!")
        except Exception as e:
            await ctx.send(f"❌ Error adding task: {e}")


# Example of how to integrate with your bot
"""
# In your main bot file:

from utils.scheduler_examples import setup_bot_scheduler

class YourBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!')
        self.scheduler = None
    
    async def setup_hook(self):
        # Setup scheduler when bot starts
        self.scheduler = await setup_bot_scheduler(self)
        
        # Add scheduler commands
        scheduler_commands = SchedulerCommands(self.scheduler)
        self.add_command(commands.Command(scheduler_commands.status_command, name='scheduler'))
        self.add_command(commands.Command(scheduler_commands.add_task_command, name='addtask'))
    
    async def close(self):
        # Stop scheduler when bot stops
        if self.scheduler:
            await self.scheduler.stop()
        await super().close()
""" 