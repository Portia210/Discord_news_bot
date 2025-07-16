"""
Bot Integration - Simple integration with Discord bot
"""

import discord
from discord.ext import commands
from utils.logger import logger
from config import Config
from scheduler.core import Scheduler
from scheduler.task_definitions import TaskDefinitions


class BotScheduler:
    """Main scheduler class for Discord bot integration"""
    
    def __init__(self, bot: discord.Client, alert_channel_id: int = None):
        self.bot = bot
        self.alert_channel_id = alert_channel_id or Config.CHANNEL_IDS.TWEETER_NEWS
        
        # Initialize components
        self.calendar_manager = CalendarManager(bot, self.alert_channel_id)
        self.task_definitions = TaskDefinitions(self.calendar_manager)
        self.scheduler = Scheduler()
        
        # Setup tasks
        self._setup_tasks()
    
    def _setup_tasks(self):
        """Setup all tasks"""
        tasks = self.task_definitions.get_all_tasks()
        for task in tasks:
            self.scheduler.add_task(task)
        
        logger.info(f"📅 Setup {len(tasks)} tasks")
    
    async def start(self):
        """Start the scheduler"""
        await self.scheduler.start()
    
    async def stop(self):
        """Stop the scheduler"""
        await self.scheduler.stop()
        await self.calendar_manager.cancel_all_dynamic_tasks()
    
    def get_status(self):
        """Get scheduler status"""
        status = self.scheduler.get_status()
        status['dynamic_tasks'] = self.calendar_manager.get_dynamic_task_count()
        return status


# Discord commands for scheduler management
class SchedulerCommands(commands.Cog):
    def __init__(self, bot_scheduler: BotScheduler):
        self.scheduler = bot_scheduler
    
    @commands.command(name="scheduler")
    async def scheduler_status(self, ctx):
        """Show scheduler status"""
        status = self.scheduler.get_status()
        
        embed = discord.Embed(
            title="📅 Scheduler Status",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Tasks",
            value=str(len(status)),
            inline=True
        )
        embed.add_field(
            name="Dynamic Tasks",
            value=str(status.get('dynamic_tasks', 0)),
            inline=True
        )
        
        # Show task details
        for task_name, task_info in status.items():
            if task_name != 'dynamic_tasks':
                status_text = f"**Next:** {task_info['next_run']}\n"
                status_text += f"**Days:** {', '.join(task_info['days'])}\n"
                status_text += f"**Time:** {task_info['time']}\n"
                status_text += f"**Running:** {'✅' if task_info['is_running'] else '❌'}"
                
                embed.add_field(
                    name=task_name,
                    value=status_text,
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="holiday")
    async def check_holiday(self, ctx):
        """Manually check for holidays today"""
        await ctx.send("🔍 Checking for holidays...")
        
        is_holiday = await self.scheduler.calendar_manager.check_holiday_calendar()
        
        if is_holiday:
            await ctx.send("🎉 Holiday detected today!")
        else:
            await ctx.send("✅ No holidays today")
    
    @commands.command(name="events")
    async def check_events(self, ctx):
        """Manually check economic events for today"""
        await ctx.send("📊 Fetching economic events...")
        
        events = await self.scheduler.calendar_manager.get_economic_events()
        
        if events:
            embed = discord.Embed(
                title="📅 Today's Economic Events",
                color=0x00ff00
            )
            
            for event in events:
                embed.add_field(
                    name=f"{event.time_str} - {event.importance.upper()}",
                    value=event.name,
                    inline=False
                )
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("📅 No economic events scheduled for today")


