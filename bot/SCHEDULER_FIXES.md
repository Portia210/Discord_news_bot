# Scheduler Fixes

## Issues Fixed

### 1. Tasks Blocking Each Other

**Problem**: When multiple tasks were scheduled close together (e.g., news at 23:00:00 and calendar at 23:00:03), the first task would block the second from running on time.

**Root Cause**: APScheduler was configured with limited concurrency (`max_instances: 3`) and no grace period for missed jobs.

**Solution**:
- Increased `max_instances` from 3 to 10 to allow more concurrent jobs
- Added `misfire_grace_time: 60` to allow jobs to run up to 60 seconds late
- Added job listener to monitor and alert on missed jobs

**Files Modified**:
- `scheduler_v2/discord_scheduler.py`: Updated job defaults and added job listener

### 2. Economic Calendar Only Runs Once

**Problem**: The economic calendar task would remove the daily cron job (`economic_calendar_check`) and not recreate it, causing it to only run once.

**Root Cause**: The task was removing ALL jobs starting with 'economic_' including the daily cron job.

**Solution**:
- Modified job removal logic to exclude the daily cron job (`economic_calendar_check`)
- Added logic to recreate the daily cron job if it's missing
- Ensured the daily job persists across task executions

**Files Modified**:
- `scheduler_v2/tasks/economic_calendar_tasks.py`: Updated job removal logic and added job recreation

## Changes Made

### DiscordScheduler Class

```python
# Before
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

# After  
job_defaults = {
    'coalesce': False,
    'max_instances': 10,  # Allow more concurrent jobs
    'misfire_grace_time': 60  # Allow jobs to run up to 60 seconds late
}
```

### Job Listener Added

```python
def _job_listener(self, event):
    """Handle job events for monitoring"""
    if event.code == 4096:  # EVENT_JOB_MISSED
        logger.warning(f"⚠️ Job missed: {event.job_id}")
        # Send alert for missed jobs
        asyncio.create_task(self.send_dev_alert(...))
```

### Economic Calendar Task

```python
# Before: Removed ALL economic jobs
for job in existing_jobs:
    if job.id.startswith('economic_'):
        discord_scheduler.remove_job(job.id)

# After: Preserve daily cron job
for job in existing_jobs:
    if job.id.startswith('economic_') and not job.id == 'economic_calendar_check':
        discord_scheduler.remove_job(job.id)

# Added: Ensure daily job exists
daily_job = discord_scheduler.get_job('economic_calendar_check')
if not daily_job:
    # Recreate the daily cron job
    discord_scheduler.add_cron_job(...)
```

## Testing

Run the test script to verify fixes:

```bash
cd bot
python test_scheduler_fixes.py
```

## Expected Behavior After Fixes

1. **Concurrent Execution**: Jobs scheduled close together will run concurrently instead of blocking each other
2. **Grace Period**: Jobs that are slightly late will still run (up to 60 seconds)
3. **Missed Job Alerts**: You'll get Discord alerts when jobs are missed
4. **Daily Job Persistence**: The economic calendar will run every weekday at 8:00 AM consistently
5. **Better Logging**: More detailed logging about job execution and missed jobs

## Monitoring

The scheduler now provides better monitoring:
- Job execution logs
- Missed job warnings
- Discord alerts for scheduler issues
- Job summary with next run times

Check the logs for:
- `⚠️ Job missed:` - Indicates a job was missed
- `📅 Recreating daily economic calendar cron job` - Shows daily job recreation
- `🚀 Executing job:` - Shows job execution
- `✅ Job completed:` - Shows successful completion 