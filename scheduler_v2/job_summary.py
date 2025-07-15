"""
Job Summary Module - Handles job summary generation and formatting
"""

from datetime import datetime
from typing import List, Dict, Any
from utils.logger import logger


class JobSummary:
    """Handles job summary generation and formatting"""
    
    def __init__(self, timezone):
        self.timezone = timezone
        self.jobs_added = []
    
    def add_job(self, job_data: Dict[str, Any]):
        """Add a job to the summary tracking"""
        self.jobs_added.append(job_data)
    
    def clear_jobs(self):
        """Clear all tracked jobs"""
        self.jobs_added.clear()
    
    def get_job_count(self) -> int:
        """Get total number of tracked jobs"""
        return len(self.jobs_added)
    
    def _sort_cron_jobs(self, cron_jobs: List[Dict]) -> List[Dict]:
        """Sort cron jobs by execution time"""
        def sort_key(job):
            parts = job['expression'].split()
            if len(parts) >= 2:
                minute = int(parts[0]) if parts[0] != '*' else 0
                hour = int(parts[1]) if parts[1] != '*' else 0
                return hour * 60 + minute
            return 0
        
        return sorted(cron_jobs, key=sort_key)
    
    def _sort_date_jobs(self, date_jobs: List[Dict]) -> List[Dict]:
        """Sort date jobs by execution time"""
        def sort_key(job):
            try:
                return datetime.fromisoformat(job['run_date'].replace('Z', '+00:00'))
            except Exception as e:
                logger.error(f"Error sorting date jobs: {e}")
                return datetime.min
        
        return sorted(date_jobs, key=sort_key)
    
    def _format_cron_time(self, cron_expression: str) -> str:
        """Format cron expression to readable time"""
        parts = cron_expression.split()
        if len(parts) >= 2:
            minute = parts[0] if parts[0] != '*' else '0'
            hour = parts[1] if parts[1] != '*' else '0'
            return f"{hour.zfill(2)}:{minute.zfill(2)}"
        return "00:00"
    
    def generate_summary(self) -> str:
        """Generate a comprehensive summary of all scheduled jobs"""
        if not self.jobs_added:
            return "No jobs scheduled"
        
        summary = f"📋 **Scheduled Jobs Summary** ({len(self.jobs_added)} total)\n\n"
        
        # Group jobs by type
        cron_jobs = [job for job in self.jobs_added if job['type'] == 'cron']
        date_jobs = [job for job in self.jobs_added if job['type'] == 'date']
        interval_jobs = [job for job in self.jobs_added if job['type'] == 'interval']
        
        # Sort jobs
        cron_jobs = self._sort_cron_jobs(cron_jobs)
        date_jobs = self._sort_date_jobs(date_jobs)
        
        # Format cron jobs section
        if cron_jobs:
            summary += "🕐 **Cron Jobs (sorted by time):**\n"
            for job in cron_jobs:
                time_str = self._format_cron_time(job['expression'])
                summary += f"  • `{time_str}` - `{job['id']}` - `{job['expression']}`\n"
            summary += "\n"
        
        # Format date jobs section
        if date_jobs:
            summary += "📅 **One-time Jobs (sorted by date):**\n"
            for job in date_jobs:
                summary += f"  • `{job['id']}` - `{job['run_date']}`\n"
            summary += "\n"
        
        # Format interval jobs section
        if interval_jobs:
            summary += "⏱️ **Interval Jobs:**\n"
            for job in interval_jobs:
                summary += f"  • `{job['id']}` - every {job['seconds']} seconds\n"
            summary += "\n"
        
        summary += f"🌍 **Timezone:** {self.timezone}"
        return summary
    
    def generate_compact_summary(self) -> str:
        """Generate a compact summary for logging"""
        if not self.jobs_added:
            return "No jobs scheduled"
        
        cron_count = len([job for job in self.jobs_added if job['type'] == 'cron'])
        date_count = len([job for job in self.jobs_added if job['type'] == 'date'])
        interval_count = len([job for job in self.jobs_added if job['type'] == 'interval'])
        
        summary = f"📋 Jobs Summary: {cron_count} cron, {date_count} one-time, {interval_count} interval"
        return summary
    
    def get_jobs_by_type(self, job_type: str) -> List[Dict]:
        """Get all jobs of a specific type"""
        return [job for job in self.jobs_added if job['type'] == job_type]
    
    def get_next_job_time(self) -> str:
        """Get the next job execution time"""
        if not self.jobs_added:
            return "No jobs scheduled"
        
        # For cron jobs, find the earliest time
        cron_jobs = self.get_jobs_by_type('cron')
        if cron_jobs:
            sorted_cron = self._sort_cron_jobs(cron_jobs)
            earliest_time = self._format_cron_time(sorted_cron[0]['expression'])
            return f"Next cron job: {earliest_time} ({sorted_cron[0]['id']})"
        
        # For date jobs, find the earliest date
        date_jobs = self.get_jobs_by_type('date')
        if date_jobs:
            sorted_dates = self._sort_date_jobs(date_jobs)
            return f"Next one-time job: {sorted_dates[0]['run_date']} ({sorted_dates[0]['id']})"
        
        return "No time-based jobs found" 