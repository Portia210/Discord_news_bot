# Scheduler System

A clean, scalable scheduler system for Discord bot tasks with calendar integration.

## 📁 Structure

```
scheduler/
├── __init__.py           # Package exports
├── core.py              # Main scheduler class
├── tasks.py             # Task and TaskCondition classes
├── calendar_manager.py  # Holiday and economic calendar handling
├── task_definitions.py  # Define all your tasks here
├── bot_integration.py   # Discord bot integration
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from scheduler.bot_integration import BotScheduler, SchedulerCommands

class YourBot(commands.Bot):
    async def setup_hook(self):
        # Initialize scheduler
        self.bot_scheduler = BotScheduler(
            bot=self,
            alert_channel_id=YOUR_ALERT_CHANNEL_ID
        )
        
        # Start scheduler
        await self.bot_scheduler.start()
        
        # Add commands
        await self.add_cog(SchedulerCommands(self.bot_scheduler))
    
    async def close(self):
        if self.bot_scheduler:
            await self.bot_scheduler.stop()
        await super().close()
```

### 2. Add New Tasks

Edit `task_definitions.py`:

```python
async def my_new_task(self):
    # Your task logic here
    logger.info("Running my new task")
    await self.calendar_manager.send_alert("Task completed!", 0x00ff00)

def get_all_tasks(self) -> list[Task]:
    return [
        # ... existing tasks ...
        
        # Add your new task
        Task(
            name="my_new_task",
            func=self.my_new_task,
            time_str="15:30",
            days=parse_days("mon-fri")
        )
    ]
```

## 📅 Features

### ✅ Daily Schedule (Mon-Fri)
- **8:00 AM**: Check holidays → Cancel tasks if holiday found
- **9:30 AM**: Market open check
- **2:30 PM**: Daily report
- **Dynamic**: Economic events scheduled 5 minutes before each event

### ✅ Weekly Schedule
- **Sunday 9:00 AM**: Weekly backup

### ✅ Holiday Detection
- Automatically checks holiday calendar
- Cancels daily tasks if holiday found
- Sends Discord alerts

### ✅ Economic Events
- Fetches economic calendar daily
- Creates dynamic tasks for each event
- Sends alerts with event results

## 🎮 Discord Commands

- `!scheduler` - Show scheduler status
- `!holiday` - Manually check for holidays
- `!events` - Show today's economic events

## 🔧 Configuration

### Timezone
Uses your config timezone automatically:
```python
# In config.py
self.app_timezone = pytz.timezone('Asia/Jerusalem')
```

### Alert Channel
Set your alert channel ID:
```python
alert_channel_id = YOUR_DISCORD_CHANNEL_ID
```

## 📝 Adding Tasks

### Simple Task
```python
Task(
    name="task_name",
    func=self.task_function,
    time_str="14:30",
    days=parse_days("mon-fri")
)
```

### Task with Conditions
```python
Task(
    name="conditional_task",
    func=self.task_function,
    time_str="09:00",
    days=parse_days("mon-fri"),
    conditions=[
        create_condition("market_closed", self.check_market_closed)
    ]
)
```

### Day Formats
```python
parse_days("mon-fri")     # Monday to Friday
parse_days("mon,wed,fri") # Specific days
parse_days("sat-sun")     # Weekend
```

## 🛠️ Customization

### Add New Calendar Types
Edit `calendar_manager.py` to add support for other calendar types.

### Add New Conditions
Create custom conditions in `task_definitions.py`:
```python
async def custom_condition(self):
    # Your condition logic
    return True  # Return True to cancel task

# Use in task:
conditions=[create_condition("custom", self.custom_condition)]
```

### Modify Alert Messages
Edit the alert functions in `calendar_manager.py` to customize Discord messages.

## 🔍 Troubleshooting

### Task Not Running
1. Check timezone settings
2. Verify day format (mon, tue, etc.)
3. Check logs for errors

### Calendar Not Working
1. Verify investing scraper is working
2. Check network connectivity
3. Verify calendar data format

### Discord Alerts Not Sending
1. Check channel ID is correct
2. Verify bot has permissions
3. Check bot is in the channel

## 📊 Monitoring

Use the `!scheduler` command to monitor:
- Task status
- Next run times
- Dynamic task count
- Running status

## 🔄 Scalability

The system is designed to be easily scalable:
- Add new tasks in `task_definitions.py`
- Add new calendar types in `calendar_manager.py`
- Add new conditions as needed
- All components are modular and independent 