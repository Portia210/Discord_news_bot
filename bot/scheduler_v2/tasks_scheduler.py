"""
Task Manager - Extends DiscordScheduler with task management functionality
"""

from datetime import datetime, timedelta, time
import pandas as pd
from utils.logger import logger
from my_api.market_schedule import get_market_schedule_for_next_quarter
from .tasks.news_report import (
    morning_news_report_task,
    evening_news_report_task
)
from .tasks.economic_calendar.economic_calendar_daily_task import schedule_economic_calendar_task
from config import Config
from .core_scheduler import CoreScheduler


class TasksScheduler(CoreScheduler):
    """DiscordScheduler with task management capabilities"""
    
    def __init__(self, bot, alert_channel_id: int, dev_channel_id: int, timezone: str, post_event_delay: int = 3, schedule: Config.SCHEDULE = None):
        """Initialize TasksScheduler with DiscordScheduler functionality"""
        super().__init__(bot, alert_channel_id, dev_channel_id, timezone, post_event_delay, schedule)
        # Ensure the global scheduler points to this TasksScheduler instance
        from .global_scheduler import set_discord_scheduler
        set_discord_scheduler(self)
    
    async def setup_all_tasks(self):
        """Setup all scheduled tasks"""
        logger.info("📅 Setting up all scheduled tasks...")
        
        try:
            await self._startup_setup()
            await self._daily_setup()
            await self._weekly_setup()
            
        except Exception as e:
            logger.error(f"❌ Error setting up tasks: {str(e)}")
            raise

    async def _startup_setup(self):
        """Setup startup tasks"""
        try:
            current_time = datetime.now(self.timezone)
            setup_time = self.schedule.DAILY_SETUP.time
            
            if current_time.time() >= setup_time:
                logger.info(f"🌅 Running economic calendar startup task")
                await schedule_economic_calendar_task()
            else:
                logger.info(f"🌙 Skipping startup task, waiting for daily cron job")
        except Exception as e:
            logger.error(f"❌ Error in startup setup: {str(e)}")
            raise
    
    async def _daily_setup(self):
        """Setup daily gatekeeper task"""
        try:
            # Daily gatekeeper task - runs first thing in the morning
            self.add_cron_job(
                func=self._daily_gatekeeper,
                cron_expression=f"{self.schedule.DAILY_SETUP.minute} {self.schedule.DAILY_SETUP.hour} * * *",
                job_id="daily_gatekeeper"
            )
            
            logger.debug("✅ Daily gatekeeper scheduled")
        except Exception as e:
            logger.error(f"❌ Error setting up daily tasks: {str(e)}")
            raise

    async def _weekly_setup(self):
        """Setup weekly recurring tasks"""
        try:
            # TODO: Add weekly tasks here
            logger.info("✅ Weekly tasks setup completed (no tasks configured)")
        except Exception as e:
            logger.error(f"❌ Error setting up weekly tasks: {str(e)}")
            raise

    async def _daily_gatekeeper(self):
        """Main gatekeeper that checks conditions and sets up today's tasks"""
        try:
            logger.info("🚪 Daily gatekeeper starting...")
            
            # Get market schedule
            market_schedule = await get_market_schedule_for_next_quarter(Config.TIMEZONES.APP_TIMEZONE)
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            if today_date not in market_schedule['date'].values:
                logger.info("🚨 Today is not a market day - skipping tasks")
                return
            
            # Get today's data
            today_data = market_schedule.loc[market_schedule['date'] == today_date].to_dict(orient='records')[0]
            market_open = datetime.strptime(today_data["open_time"], "%H:%M").time() if today_data["open_time"] is not None else None
            market_close = datetime.strptime(today_data["close_time"], "%H:%M").time() if today_data["close_time"] is not None else None
            
            # Check if today is a holiday
            if pd.notna(today_data.get('holiday')):
                logger.info(f"🏖️ Holiday detected: {today_data.get('holiday', 'Unknown holiday')}")
                if market_open is None:
                    await self._setup_full_holiday_tasks()
                else:
                    await self._setup_partial_holiday_tasks(market_open, market_close)
            else:
                logger.info("📈 Regular market day detected")
                await self._setup_regular_day_tasks(market_open, market_close)
                
        except Exception as e:
            logger.error(f"❌ Error in daily gatekeeper: {str(e)}")
            raise

    async def _setup_full_holiday_tasks(self):
        """Setup tasks for holiday days (currently empty)"""
        try:
            logger.info("🏖️ Setting up full holiday tasks (no tasks scheduled)")
            # TODO: Setup holiday tasks, send alert to dev channel, send notification to users, send night news report
            pass
        except Exception as e:
            logger.error(f"❌ Error setting up full holiday tasks: {str(e)}")
            raise

    async def _setup_partial_holiday_tasks(self, market_open: time, market_close: time):
        """Setup tasks for partial holiday days (currently empty)"""
        try:
            logger.info(f"🏖️ Setting up partial holiday tasks - Market open: {market_open}, close: {market_close}")
            # TODO: Setup holiday tasks, send alert to dev channel, send notification to users
            await self._setup_regular_day_tasks(market_open, market_close)
        except Exception as e:
            logger.error(f"❌ Error setting up partial holiday tasks: {str(e)}")
            raise

    async def _setup_regular_day_tasks(self, market_open: time, market_close: time):
        """Setup regular daily tasks with market times"""
        try:
            logger.info(f"📅 Setting up regular tasks for today")
            
            # Calculate task times based on market times
            today = datetime.now(self.timezone).date()
            market_open_dt = datetime.combine(today, market_open)
            market_close_dt = datetime.combine(today, market_close)
            
            morning_news_time = market_open_dt - timedelta(minutes=30)  # 30 minutes before market open
            evening_news_time = market_close_dt + timedelta(minutes=1)  # 1 minute after market close
            
            # Parse economic calendar time
            economic_calendar_time = self.schedule.DAILY_ECONOMIC_CALENDAR.time
            economic_calendar_datetime = datetime.now(self.timezone).replace(
                hour=economic_calendar_time.hour,
                minute=economic_calendar_time.minute,
                second=economic_calendar_time.second,
                microsecond=0
            )

            logger.info(f"📋 DAILY TASKS SCHEDULED:")
            logger.info(f"   🌅 Morning news report: {morning_news_time.strftime('%H:%M')}")
            logger.info(f"   🌙 Evening news report: {evening_news_time.strftime('%H:%M')}")
            logger.info(f"   📊 Economic calendar: {economic_calendar_datetime.strftime('%H:%M')}")
            
            # Morning news report
            self.add_date_job(
                func=morning_news_report_task,
                run_date=morning_news_time,
                job_id="morning_news_report_today"
            )
            
            # Evening news report
            self.add_date_job(
                func=evening_news_report_task,
                run_date=evening_news_time,
                job_id="evening_news_report_today"
            )
            
            # Economic calendar
            self.add_date_job(
                func=schedule_economic_calendar_task,
                run_date=economic_calendar_datetime,
                job_id="economic_calendar_today"
            )
            
            logger.info("✅ Regular day tasks scheduled successfully")
            
        except Exception as e:
            logger.error(f"❌ Error setting up regular day tasks: {str(e)}")
            raise 