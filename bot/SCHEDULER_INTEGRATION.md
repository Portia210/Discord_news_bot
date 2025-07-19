# Scheduler Integration Guide

## Overview
The scheduler has been integrated into your Discord bot (`bot.py`) and will run in the background automatically. It provides:

- **Daily Calendar Management**: Checks holidays and schedules economic events
- **Custom Tasks**: Morning greetings, evening summaries, news checks, and system health checks
- **Background Operation**: No Discord commands needed - runs silently in the background

## What's Running

### Calendar Tasks (Automatic)
- **Daily Schedule** (8:00 AM weekdays): Checks holidays and schedules economic events
- **Weekly Backup** (Sunday 9:00 AM): Performs weekly backup operations
- **Market Open Check** (9:30 AM weekdays): Checks market status
- **Daily Report** (2:30 PM weekdays): Generates daily reports

### Custom Tasks (Your Bot)
- **Morning Greeting** (7:00 AM weekdays): Sends morning greeting to channel
- **Evening Summary** (5:00 PM weekdays): Sends trading day summary
- **News Check** (10:00 AM weekdays): Checks for news updates
- **News Check** (12:00 PM weekdays): Checks for news updates
- **News Check** (2:00 PM weekdays): Checks for news updates
- **News Check** (4:00 PM weekdays): Checks for news updates
- **System Health Check** (6:00 AM weekdays): Performs system health monitoring

## How It Works

1. **Bot Startup**: When your bot starts, it automatically initializes the scheduler
2. **Background Operation**: The scheduler runs in the background using Discord's event loop
3. **Automatic Alerts**: All tasks send alerts to your `investing_bot` channel
4. **Error Handling**: All tasks have proper error handling and logging

## Configuration

### Channel Configuration
The scheduler sends alerts to the channel defined in `config.py`:
```python
self.investing_bot = 1389349923962491061  # Your channel ID
```

### Timezone Configuration
Uses the timezone defined in `config.py`:
```python
self.app_timezone = self.israel_timezone  # Asia/Jerusalem
```

## Adding New Tasks

### Method 1: Add to Custom Tasks
Edit `scheduler/custom_tasks.py` and add your task:

```python
async def my_new_task(self):
    """My custom task"""
    try:
        logger.info("🔄 Running my new task...")
        # Your task logic here
        await self.calendar_manager.send_alert("✅ Task completed!", 0x00ff00)
    except Exception as e:
        logger.error(f"❌ Error: {e}")

def get_custom_tasks(self) -> list[Task]:
    return [
        # ... existing tasks ...
        
        # Add your new task
        Task(
            name="my_new_task",
            func=self.my_new_task,
            time_str="15:30",  # 3:30 PM
            days=parse_days("mon-fri")  # Weekdays only
        )
    ]
```

### Method 2: Add Directly in bot.py
Add tasks directly in the `on_ready` event:

```python
# In the on_ready event, after calendar_manager.initialize():
async def my_task():
    # Your task logic here
    pass

scheduler.add_task(Task(
    name="my_task",
    func=my_task,
    time_str="16:00",
    days=["mon", "wed", "fri"]
))
```

## Task Scheduling Options

### Time Formats
- Single time: `"08:00"`
- Multiple times: `"08:00,12:00,16:00"`
- Every hour: `"09:00,10:00,11:00,12:00,13:00,14:00,15:00,16:00"`

### Day Formats
- Single day: `["mon"]`
- Multiple days: `["mon", "wed", "fri"]`
- Weekdays: `parse_days("mon-fri")`
- All days: `parse_days("mon-sun")`

### Conditions
Add conditions to cancel tasks:

```python
def market_closed_condition():
    # Return True to cancel the task
    return is_market_closed()

Task(
    name="market_task",
    func=market_task,
    time_str="09:30",
    days=parse_days("mon-fri"),
    condition=market_closed_condition
)
```

## Monitoring

### Logs
All scheduler activity is logged with emojis:
- ✅ Success
- ❌ Error
- 🚀 Starting task
- 🛑 Task cancelled

### Discord Alerts
All tasks send colored alerts to your channel:
- 🟢 Green (0x00ff00): Success
- 🔴 Red (0xff0000): Error
- 🟠 Orange (0xffa500): Warning
- 🔵 Blue (0x0000ff): Info

## Troubleshooting

### Common Issues

1. **Scheduler not starting**: Check logs for initialization errors
2. **Tasks not running**: Verify timezone and day settings
3. **Alerts not sending**: Check channel ID in config.py
4. **Import errors**: Ensure all dependencies are installed

### Debug Mode
Enable debug logging by modifying the logger level in `utils/logger.py`

## Files Structure

```
scheduler/
├── __init__.py              # Package initialization
├── core.py                  # Main scheduler engine
├── tasks.py                 # Task and condition classes
├── calendar_manager.py      # Calendar integration
├── task_definitions.py      # Built-in calendar tasks
├── custom_tasks.py          # Your custom tasks
├── bot_integration.py       # Discord bot integration
└── README.md               # Detailed documentation
```

## Next Steps

1. **Test the integration**: Run your bot and check the logs
2. **Customize tasks**: Modify `custom_tasks.py` to add your specific tasks
3. **Monitor performance**: Watch the logs and Discord alerts
4. **Extend functionality**: Add more complex conditions and tasks as needed

The scheduler is now fully integrated and will start automatically when your bot runs! 