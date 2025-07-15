#!/usr/bin/env python3
"""
Test script to verify modular task structure
"""

import asyncio
from datetime import datetime
from config import config
from scheduler_v2 import DiscordScheduler, TaskDefinitions

class MockBot:
    def get_channel(self, channel_id):
        class MockChannel:
            def __init__(self, channel_id):
                self.id = channel_id
                self.name = "test_channel"
            
            async def send(self, embed):
                print(f"📨 [Discord] {embed.title}: {embed.description}")
        
        return MockChannel(channel_id)

async def test_modular_tasks():
    """Test the modular task structure"""
    print("🔍 Testing modular task structure...")
    
    # Create mock bot and scheduler
    mock_bot = MockBot()
    scheduler = DiscordScheduler(
        bot=mock_bot,
        alert_channel_id=987654321,
        dev_channel_id=123456789,
        timezone=config.app_timezone,
        post_event_delay=3  # Configurable delay for post-event updates
    )
    
    # Create task definitions
    task_definitions = TaskDefinitions(scheduler)
    
    # Setup tasks
    print("📅 Setting up tasks...")
    task_definitions.setup_all_tasks()
    
    # Show job summary
    print("\n📋 Job Summary:")
    summary = scheduler.generate_job_summary()
    print(summary)
    
    print(f"\n📊 Total jobs: {scheduler.get_job_count()}")
    
    # Test individual tasks
    print("\n🧪 Testing individual tasks...")
    
    # Test morning news report
    from scheduler_v2.tasks.news_report import morning_news_report_task
    print("Testing morning news report task...")
    await morning_news_report_task(scheduler)
    
    # Test economic calendar task
    from scheduler_v2.tasks.economic_calendar_tasks import get_economic_calendar_task
    print("Testing economic calendar task...")
    await get_economic_calendar_task(scheduler)
    
    print("\n✅ Modular task test completed!")

if __name__ == "__main__":
    asyncio.run(test_modular_tasks()) 