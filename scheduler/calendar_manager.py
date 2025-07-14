"""
Calendar Manager - Handles holiday and economic calendar operations
"""

import asyncio
from datetime import datetime, time, timedelta
from typing import List, Optional, Dict, Any
from utils.logger import logger
from config import config
from investing_scraper.InvestingDataScraper import InvestingDataScraper
from investing_scraper.investing_variables import InvestingVariables
import discord


class CalendarEvent:
    """Represents a calendar event with time"""
    
    def __init__(self, name: str, time_str: str, importance: str = "medium"):
        self.name = name
        self.time_str = time_str
        self.importance = importance
        
        # Parse time
        try:
            hour, minute = map(int, time_str.split(':'))
            self.event_time = time(hour, minute)
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}")
    
    def __str__(self):
        return f"{self.name} at {self.time_str} ({self.importance})"


class CalendarManager:
    """Manages calendar operations and dynamic task creation"""
    
    def __init__(self, bot: discord.Client, alert_channel_id: int = None):
        self.bot = bot
        self.alert_channel_id = alert_channel_id
        self.investing_scraper = InvestingDataScraper()
        self.timezone = config.app_timezone
        self.dynamic_tasks: Dict[str, asyncio.Task] = {}
    
    async def send_alert(self, message: str, color: int = 0xff0000):
        """Send alert to Discord channel"""
        if not self.alert_channel_id:
            logger.warning("No alert channel configured")
            return
            
        try:
            channel = self.bot.get_channel(self.alert_channel_id)
            if channel:
                embed = discord.Embed(
                    title="📅 Calendar Alert",
                    description=message,
                    color=color,
                    timestamp=datetime.now(self.timezone)
                )
                await channel.send(embed=embed)
            else:
                logger.error(f"Alert channel {self.alert_channel_id} not found")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def check_holiday_calendar(self) -> bool:
        """Check if today is a holiday - returns True if holiday found"""
        try:
            logger.info("🔍 Checking holiday calendar...")
            
            # Get today's date in the correct timezone
            today = datetime.now(self.timezone).strftime('%Y-%m-%d')
            
            # Fetch holiday calendar data
            payload = {
                "currentTab": InvestingVariables.TIME_RANGES.TODAY,
                "timeZone": InvestingVariables.TIME_ZONES.ISRAEL,
                "country[]": [InvestingVariables.COUNTRIES.UNITED_STATES],
            }
            
            holiday_data = await self.investing_scraper.run("holiday_calendar", payload, False)
            
            if holiday_data:
                # Check if there are any holidays today
                today_holidays = []
                for event in holiday_data:
                    if event.get('date') == today:
                        today_holidays.append(event.get('holiday', 'Unknown Holiday'))
                
                if today_holidays:
                    holiday_message = f"🎉 **Holiday Alert!**\nToday's holidays:\n"
                    for holiday in today_holidays:
                        holiday_message += f"• {holiday}\n"
                    
                    await self.send_alert(holiday_message, 0xffa500)  # Orange color
                    logger.info(f"🎉 Holiday detected: {today_holidays}")
                    return True
                else:
                    logger.info("✅ No holidays today")
                    return False
            else:
                logger.warning("⚠️ No holiday data received")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking holiday calendar: {e}")
            return False
    
    async def get_economic_events(self) -> List[CalendarEvent]:
        """Get economic events for today and create CalendarEvent objects"""
        try:
            logger.info("📊 Fetching economic calendar events...")
            
            # Get today's date
            today = datetime.now(self.timezone).strftime('%Y-%m-%d')
            
            # Fetch economic calendar data
            payload = {
                "currentTab": InvestingVariables.TIME_RANGES.TODAY,
                "timeZone": InvestingVariables.TIME_ZONES.ISRAEL,
                "importance[]": [
                    InvestingVariables.IMPORTANCE.HIGH,
                    InvestingVariables.IMPORTANCE.MEDIUM
                ],
                "country[]": [InvestingVariables.COUNTRIES.UNITED_STATES],
            }
            
            economic_data = await self.investing_scraper.run("economic_calendar", payload, False)
            
            events = []
            if economic_data:
                for event in economic_data:
                    event_time = event.get('time', '')
                    if event_time and event.get('date') == today:
                        event_name = event.get('description', 'Unknown Event')
                        importance = event.get('volatility', 'medium')
                        
                        # Create CalendarEvent
                        calendar_event = CalendarEvent(
                            name=event_name,
                            time_str=event_time,
                            importance=importance
                        )
                        events.append(calendar_event)
                        
                        logger.info(f"📅 Found event: {calendar_event}")
            
            logger.info(f"📊 Found {len(events)} economic events for today")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error fetching economic events: {e}")
            return []
    
    async def create_economic_event_task(self, event: CalendarEvent):
        """Create a dynamic task for an economic event"""
        async def economic_event_task():
            try:
                logger.info(f"📊 Executing economic event task: {event}")
                
                # Fetch updated economic data for this specific time
                payload = {
                    "currentTab": InvestingVariables.TIME_RANGES.TODAY,
                    "timeZone": InvestingVariables.TIME_ZONES.ISRAEL,
                    "importance[]": [
                        InvestingVariables.IMPORTANCE.HIGH,
                        InvestingVariables.IMPORTANCE.MEDIUM
                    ],
                    "country[]": [InvestingVariables.COUNTRIES.UNITED_STATES],
                }
                
                updated_data = await self.investing_scraper.run("economic_calendar", payload, False)
                
                # Process the updated data
                if updated_data:
                    # Find the specific event
                    for data_event in updated_data:
                        if (data_event.get('description') == event.name and 
                            data_event.get('time') == event.time_str):
                            
                            # Create alert message
                            alert_msg = f"📊 **Economic Event Update**\n"
                            alert_msg += f"**Event:** {event.name}\n"
                            alert_msg += f"**Time:** {event.time_str}\n"
                            alert_msg += f"**Importance:** {event.importance}\n"
                            
                            if data_event.get('actual'):
                                alert_msg += f"**Actual:** {data_event['actual']}\n"
                            if data_event.get('forecast'):
                                alert_msg += f"**Forecast:** {data_event['forecast']}\n"
                            if data_event.get('previous'):
                                alert_msg += f"**Previous:** {data_event['previous']}\n"
                            
                            await self.send_alert(alert_msg, 0x00ff00)  # Green color
                            break
                
            except Exception as e:
                logger.error(f"❌ Error in economic event task: {e}")
        
        return economic_event_task
    
    async def schedule_economic_events(self, events: List[CalendarEvent]):
        """Schedule dynamic tasks for economic events"""
        # Cancel existing dynamic tasks
        for task_name, task in self.dynamic_tasks.items():
            task.cancel()
            logger.info(f"🛑 Cancelled existing dynamic task: {task_name}")
        
        self.dynamic_tasks.clear()
        
        # Create new tasks for each event
        now = datetime.now(self.timezone)
        for event in events:
            # Calculate when to run this task (5 minutes before event)
            event_hour, event_minute = map(int, event.time_str.split(':'))
            event_time = time(event_hour, event_minute)
            
            # Schedule 5 minutes before
            task_time = datetime.combine(now.date(), event_time, tzinfo=self.timezone) - timedelta(minutes=5)
            
            if task_time > now:
                # Create and schedule the task
                task_func = await self.create_economic_event_task(event)
                task_name = f"economic_{event.name}_{event.time_str}"
                
                # Schedule the task
                self.dynamic_tasks[task_name] = asyncio.create_task(
                    self._schedule_single_task(task_func, task_time, task_name)
                )
                
                logger.info(f"📅 Scheduled economic event task: {task_name} at {task_time.strftime('%H:%M')}")
    
    async def _schedule_single_task(self, task_func, run_time: datetime, task_name: str):
        """Schedule a single task to run at a specific time"""
        try:
            wait_seconds = (run_time - datetime.now(self.timezone)).total_seconds()
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            
            await task_func()
            
        except Exception as e:
            logger.error(f"❌ Error in scheduled task {task_name}: {e}")
        finally:
            # Clean up the task
            if task_name in self.dynamic_tasks:
                del self.dynamic_tasks[task_name]
    
    def get_dynamic_task_count(self) -> int:
        """Get number of active dynamic tasks"""
        return len(self.dynamic_tasks)
    
    async def cancel_all_dynamic_tasks(self):
        """Cancel all dynamic tasks"""
        for task_name, task in self.dynamic_tasks.items():
            task.cancel()
            logger.info(f"🛑 Cancelled dynamic task: {task_name}")
        self.dynamic_tasks.clear() 