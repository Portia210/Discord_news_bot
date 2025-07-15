# DiscordScheduler & APScheduler Guide

## 📋 Overview

The `DiscordScheduler` is a wrapper around APScheduler that provides Discord integration for scheduling tasks. It handles job management, timezone support, and Discord notifications.

## 🏗️ Architecture

```
DiscordScheduler
├── APScheduler (Core scheduling engine)
├── JobSummary (Job tracking and reporting)
├── Discord Integration (Dev alerts)
└── Timezone Management
```

## 🔧 APScheduler Core Concepts

### What is APScheduler?

APScheduler (Advanced Python Scheduler) is a Python library that lets you schedule Python functions to be executed at specific times. Think of it as a "smart alarm clock" for your code.

### Key APScheduler Components

#### 1. **Scheduler**
The main orchestrator that manages all jobs.

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(
    timezone=timezone,  # Timezone for all jobs
    jobstores={'default': MemoryJobStore()},  # Where jobs are stored
    executors={'default': AsyncIOExecutor()},  # How jobs are executed
    job_defaults={'coalesce': False, 'max_instances': 3}  # Job behavior
)
```

#### 2. **Job Stores**
Where scheduled jobs are persisted. We use `MemoryJobStore` (jobs lost on restart).

**Other options:**
- `SQLAlchemyJobStore` - Database storage
- `RedisJobStore` - Redis storage
- `MongoDBJobStore` - MongoDB storage

#### 3. **Executors**
How jobs are executed. We use `AsyncIOExecutor` for async functions.

**Other options:**
- `ThreadPoolExecutor` - Thread-based execution
- `ProcessPoolExecutor` - Process-based execution

#### 4. **Triggers**
Define WHEN jobs should run.

### 🔥 Trigger Types

#### **CronTrigger** - Time-based scheduling
```python
from apscheduler.triggers.cron import CronTrigger

# Cron expression: "minute hour day month day_of_week"
trigger = CronTrigger.from_crontab("0 8 * * 1-5")  # 8 AM weekdays
trigger = CronTrigger(minute=30, hour=14, day_of_week="mon-fri")  # 2:30 PM weekdays
```

**Cron Expression Format:**
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

**Common Examples:**
- `"0 8 * * 1-5"` - 8:00 AM Monday-Friday
- `"30 14 * * *"` - 2:30 PM daily
- `"0 9 * * 0"` - 9:00 AM Sundays
- `"0 12 1 * *"` - 12:00 PM on 1st of month
- `"0 0 1 1 *"` - Midnight on New Year's Day

#### **DateTrigger** - One-time execution
```python
from apscheduler.triggers.date import DateTrigger
from datetime import datetime

# Run at specific date/time
trigger = DateTrigger(run_date=datetime(2025, 7, 15, 14, 30))
trigger = DateTrigger(run_date="2025-07-15 14:30:00")
```

#### **IntervalTrigger** - Recurring intervals
```python
from apscheduler.triggers.interval import IntervalTrigger

# Run every X seconds/minutes/hours
trigger = IntervalTrigger(seconds=60)  # Every minute
trigger = IntervalTrigger(minutes=30)  # Every 30 minutes
trigger = IntervalTrigger(hours=2)     # Every 2 hours
```

## 🚀 DiscordScheduler Implementation

### Initialization
```python
scheduler = DiscordScheduler(
    bot=discord_bot,
    dev_channel_id=123456789,  # Channel for dev alerts
    timezone=pytz.timezone('Asia/Jerusalem')
)
```

### Job Management Methods

#### 1. **add_cron_job()** - Schedule recurring tasks
```python
scheduler.add_cron_job(
    func=my_task_function,
    cron_expression="0 8 * * 1-5",  # 8 AM weekdays
    job_id="daily_morning_task",
    args=(param1, param2),
    kwargs={'key': 'value'},
    send_alert=True  # Send Discord notification on completion
)
```

#### 2. **add_date_job()** - Schedule one-time tasks
```python
future_time = datetime.now() + timedelta(hours=2)
scheduler.add_date_job(
    func=my_task_function,
    run_date=future_time,
    job_id="one_time_task",
    send_alert=True
)
```

#### 3. **add_interval_job()** - Schedule interval-based tasks
```python
scheduler.add_interval_job(
    func=my_task_function,
    job_id="periodic_task",
    seconds=300,  # Every 5 minutes
    send_alert=True
)
```

### Job Execution Flow

```
1. Job Triggered (Cron/Date/Interval)
   ↓
2. Wrapped Function Executed
   ↓
3. Task Function Runs
   ↓
4. Success/Error Handling
   ↓
5. Discord Alert Sent (if enabled)
   ↓
6. Logging
```

### Error Handling
```python
async def wrapped_func():
    try:
        # Execute the actual task
        result = await func(*args, **kwargs)
        
        # Send success alert
        if send_alert:
            await self.send_dev_alert(f"✅ {job_id} completed", 0x00ff00)
        
    except Exception as e:
        # Send error alert
        if send_alert:
            await self.send_dev_alert(f"❌ {job_id} failed: {e}", 0xff0000)
```

## 🕐 Timezone Management

### Why Timezones Matter
- **Server timezone** might be UTC
- **Your timezone** might be different (e.g., Asia/Jerusalem)
- **APScheduler** needs to know which timezone to use for scheduling

### Timezone Configuration
```python
# In config.py
self.app_timezone = pytz.timezone('Asia/Jerusalem')

# In DiscordScheduler
self.timezone = timezone  # Passed from config
self.scheduler = AsyncIOScheduler(timezone=self.timezone)
```

### CronTrigger with Timezone
```python
# CRITICAL: Always pass timezone to CronTrigger
CronTrigger.from_crontab("0 8 * * 1-5", timezone=self.timezone)
# Without timezone, it defaults to UTC!
```

## 📊 Job Summary System

### JobSummary Class
Tracks all scheduled jobs and generates formatted summaries.

```python
job_summary = JobSummary(timezone)

# Add jobs as they're scheduled
job_summary.add_job({
    'id': 'daily_task',
    'type': 'cron',
    'expression': '0 8 * * 1-5',
    'timezone': 'Asia/Jerusalem'
})

# Generate sorted summary
summary = job_summary.generate_summary()
```

### Summary Features
- **Time-based sorting** for cron jobs
- **Date-based sorting** for one-time jobs
- **Grouped by type** (Cron, Date, Interval)
- **Readable time format** (06:00, 14:30, etc.)

## 🔔 Discord Integration

### Dual-Channel System
- **Dev Channel**: Scheduler status, errors, job summaries
- **Alert Channel**: Actual data, market updates, user-facing messages

### Alert Methods
```python
# Dev alerts (scheduler status)
await scheduler.send_dev_alert("Scheduler started", 0x00ff00)

# Data alerts (actual content)
await scheduler.send_alert("Market data update", 0x00ff00)
```

## 🛠️ Usage Examples

### Basic Daily Task
```python
async def daily_report():
    # Generate daily report
    report = await generate_report()
    
    # Send to main channel
    await scheduler.send_alert(report, 0x00ff00, "📊 Daily Report")

# Schedule for 2:30 PM weekdays
scheduler.add_cron_job(
    func=daily_report,
    cron_expression="30 14 * * 1-5",
    job_id="daily_report",
    send_alert=False  # Don't send scheduler status, just the report
)
```

### Economic Event Scheduling
```python
async def schedule_economic_event(event_time, event_name):
    scheduler.add_date_job(
        func=notify_economic_event,
        run_date=event_time,
        job_id=f"economic_{event_name}",
        args=(event_name,),
        send_alert=True
    )
```

### Health Check
```python
async def health_check():
    # Check system health
    status = await check_system_health()
    
    if not status['healthy']:
        await scheduler.send_dev_alert(
            f"⚠️ System health issue: {status['message']}",
            0xffa500,
            "🏥 Health Check"
        )

# Run every 30 minutes
scheduler.add_interval_job(
    func=health_check,
    job_id="health_check",
    seconds=1800,
    send_alert=False
)
```

## 🔧 Configuration Options

### Job Defaults
```python
job_defaults = {
    'coalesce': False,      # Don't combine missed runs
    'max_instances': 3,     # Max concurrent instances
    'misfire_grace_time': 15  # Grace period for missed jobs
}
```

### Executor Configuration
```python
executors = {
    'default': AsyncIOExecutor(max_workers=20)  # Max concurrent jobs
}
```

## 🚨 Common Issues & Solutions

### 1. **Jobs Running in Wrong Timezone**
**Problem**: Jobs run 3 hours early/late
**Solution**: Always pass timezone to CronTrigger
```python
# ❌ Wrong
CronTrigger.from_crontab("0 8 * * 1-5")

# ✅ Correct
CronTrigger.from_crontab("0 8 * * 1-5", timezone=self.timezone)
```

### 2. **Jobs Not Running**
**Problem**: Scheduler not started
**Solution**: Call `scheduler.start()`
```python
scheduler.start()  # Must be called after adding jobs
```

### 3. **Memory Issues**
**Problem**: Too many jobs in memory
**Solution**: Use database job store
```python
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}
```

### 4. **Async Function Errors**
**Problem**: Mixing sync/async functions
**Solution**: Use AsyncIOExecutor for async functions
```python
# ✅ Correct for async functions
async def my_task():
    await some_async_operation()

# ❌ Wrong - use ThreadPoolExecutor for sync functions
def my_sync_task():
    time.sleep(10)
```

## 📈 Best Practices

### 1. **Job Naming**
- Use descriptive job IDs
- Include time in name for easy identification
- Use consistent naming conventions

### 2. **Error Handling**
- Always wrap task functions in try/catch
- Log errors appropriately
- Send alerts for critical failures

### 3. **Resource Management**
- Limit concurrent job instances
- Use appropriate executors
- Monitor memory usage

### 4. **Timezone Awareness**
- Always specify timezone explicitly
- Test with different timezones
- Document timezone assumptions

### 5. **Monitoring**
- Use job summaries for overview
- Monitor job execution times
- Set up alerts for failures

## 🔍 Debugging

### Check Job Status
```python
# Get all jobs
jobs = scheduler.get_jobs()
for job in jobs:
    print(f"Job: {job.id}")
    print(f"Next run: {job.next_run_time}")
    print(f"Trigger: {job.trigger}")

# Get specific job
job = scheduler.get_job("job_id")
if job:
    print(f"Next run: {job.next_run_time}")
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Job Execution
```python
# Test job without scheduling
async def test_job():
    result = await my_task_function()
    print(f"Job result: {result}")

# Run immediately
await test_job()
```

## 📚 Additional Resources

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Cron Expression Generator](https://crontab.guru/)
- [Timezone Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)

---

This guide covers the essential concepts for working with DiscordScheduler and APScheduler. The modular design makes it easy to extend and customize for your specific needs. 