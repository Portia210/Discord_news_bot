"""
Calendar Manager V2 - Works with APScheduler-based Discord scheduler
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from utils.logger import logger
from config import config
from investing_scraper.InvestingDataScraper import InvestingDataScraper
from investing_scraper.investing_variables import InvestingVariables
from .discord_scheduler import DiscordScheduler


class CalendarEvent:
    """Represents a calendar event with specific date and time"""
    
    def __init__(self, name: str, event_date: str, event_time: str, importance: str = "medium"):
        self.name = name
        self.event_date = event_date  # YYYY-MM-DD format
        self.event_time = event_time  # HH:MM format
        self.importance = importance
        
        # Create datetime object
        try:
            date_obj = datetime.strptime(event_date, '%Y-%m-%d')
            time_obj = datetime.strptime(event_time, '%H:%M').time()
            self.event_datetime = datetime.combine(date_obj.date(), time_obj, tzinfo=config.app_timezone)
        except ValueError as e:
            raise ValueError(f"Invalid date/time format: {event_date} {event_time} - {e}")
    
    def __str__(self):
        return f"{self.name} on {self.event_date} at {self.event_time} ({self.importance})"


class CalendarManager:
    """Manages calendar operations with APScheduler integration"""
    
    def __init__(self, discord_scheduler: DiscordScheduler):
        self.discord_scheduler = discord_scheduler
        self.investing_scraper = InvestingDataScraper()
        self.timezone = config.app_timezone
        self.scheduled_events: Dict[str, CalendarEvent] = {}
    
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
                    
                    await self.discord_scheduler.send_alert(holiday_message, 0xffa500)
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
    
    async def get_economic_events(self, target_date: Optional[str] = None) -> List[CalendarEvent]:
        """Get economic events for a specific date and create CalendarEvent objects"""
        try:
            if target_date is None:
                target_date = datetime.now(self.timezone).strftime('%Y-%m-%d')
            
            logger.info(f"📊 Fetching economic calendar events for {target_date}...")
            
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
                    event_date = event.get('date', '')
                    
                    if event_time and event_date == target_date:
                        event_name = event.get('description', 'Unknown Event')
                        importance = event.get('volatility', 'medium')
                        
                        # Create CalendarEvent
                        calendar_event = CalendarEvent(
                            name=event_name,
                            event_date=event_date,
                            event_time=event_time,
                            importance=importance
                        )
                        events.append(calendar_event)
                        
                        logger.info(f"📅 Found event: {calendar_event}")
            
            logger.info(f"📊 Found {len(events)} economic events for {target_date}")
            return events
            
        except Exception as e:
            logger.error(f"❌ Error fetching economic events: {e}")
            return []
    
    async def schedule_economic_events(self, events: List[CalendarEvent]):
        """Schedule dynamic tasks for economic events using specific dates"""
        # Remove existing scheduled events
        for event_id in list(self.scheduled_events.keys()):
            self.discord_scheduler.remove_job(event_id)
            del self.scheduled_events[event_id]
        
        # Schedule new events
        now = datetime.now(self.timezone)
        for event in events:
            # Schedule 5 minutes before the event
            alert_time = event.event_datetime - timedelta(minutes=5)
            
            if alert_time > now:
                event_id = f"economic_{event.name}_{event.event_date}_{event.event_time}"
                
                # Schedule the alert
                success = self.discord_scheduler.add_date_job(
                    func=self._economic_event_alert,
                    run_date=alert_time,
                    job_id=event_id,
                    args=(event,),
                    send_alert=False  # Don't send alert for the scheduling itself
                )
                
                if success:
                    self.scheduled_events[event_id] = event
                    logger.info(f"📅 Scheduled economic event: {event_id} for {alert_time.strftime('%Y-%m-%d %H:%M')}")
                else:
                    logger.error(f"❌ Failed to schedule economic event: {event_id}")
    
    async def _economic_event_alert(self, event: CalendarEvent):
        """Handle economic event alert"""
        try:
            logger.info(f"📊 Economic event alert: {event}")
            
            # Fetch updated economic data
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
            
            # Create alert message
            alert_msg = f"📊 **Economic Event Alert**\n"
            alert_msg += f"**Event:** {event.name}\n"
            alert_msg += f"**Date:** {event.event_date}\n"
            alert_msg += f"**Time:** {event.event_time}\n"
            alert_msg += f"**Importance:** {event.importance}\n"
            
            # Add updated data if available
            if updated_data:
                for data_event in updated_data:
                    if (data_event.get('description') == event.name and 
                        data_event.get('date') == event.event_date and
                        data_event.get('time') == event.event_time):
                        
                        if data_event.get('actual'):
                            alert_msg += f"**Actual:** {data_event['actual']}\n"
                        if data_event.get('forecast'):
                            alert_msg += f"**Forecast:** {data_event['forecast']}\n"
                        if data_event.get('previous'):
                            alert_msg += f"**Previous:** {data_event['previous']}\n"
                        break
            
            await self.discord_scheduler.send_alert(alert_msg, 0x00ff00, "📊 Economic Event")
            
        except Exception as e:
            logger.error(f"❌ Error in economic event alert: {e}")
            await self.discord_scheduler.send_alert(
                f"❌ **Economic Event Alert Failed**\nEvent: {event.name}\nError: {str(e)}",
                0xff0000,
                "📊 Economic Event"
            )
    
    async def schedule_future_events(self, days_ahead: int = 7):
        """Schedule events for the next N days"""
        try:
            logger.info(f"📅 Scheduling events for next {days_ahead} days...")
            
            for i in range(days_ahead):
                target_date = (datetime.now(self.timezone) + timedelta(days=i)).strftime('%Y-%m-%d')
                events = await self.get_economic_events(target_date)
                
                if events:
                    await self.schedule_economic_events(events)
            
            logger.info(f"✅ Scheduled events for next {days_ahead} days")
            
        except Exception as e:
            logger.error(f"❌ Error scheduling future events: {e}")
    
    def get_scheduled_events_count(self) -> int:
        """Get number of scheduled economic events"""
        return len(self.scheduled_events)
    
    def get_scheduled_events(self) -> Dict[str, CalendarEvent]:
        """Get all scheduled economic events"""
        return self.scheduled_events.copy()
    
    async def clear_all_scheduled_events(self):
        """Clear all scheduled economic events"""
        for event_id in list(self.scheduled_events.keys()):
            self.discord_scheduler.remove_job(event_id)
            del self.scheduled_events[event_id]
        
        logger.info("🗑️ Cleared all scheduled economic events") 