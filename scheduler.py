import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

# Import main automation function (will be defined in main.py)
from main import run_automation_cycle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutomationScheduler:
    """Schedules and runs the YouTube automation every 288 minutes."""
    
    def __init__(self, interval_minutes=288):
        """
        Initialize the scheduler.
        
        Args:
            interval_minutes: How often to run automation (default: 288 = 4.8 hours)
        """
        self.interval_minutes = interval_minutes
        self.scheduler = BlockingScheduler(timezone='UTC')
        
        # Track job statistics
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
    
    def job_wrapper(self):
        """Wrapper function that executes the automation cycle with error handling."""
        self.total_runs += 1
        job_start = datetime.now()
        
        logger.info(f"=== Starting automation cycle #{self.total_runs} ===")
        logger.info(f"Scheduled interval: Every {self.interval_minutes} minutes")
        
        try:
            # Run the main automation cycle
            result = run_automation_cycle()
            
            if result and result.get('status') == 'success':
                self.successful_runs += 1
                logger.info(f"✓ Automation cycle completed successfully")
                logger.info(f"  - Video uploaded: {result.get('video_url', 'N/A')}")
                logger.info(f"  - Title: {result.get('title', 'N/A')}")
            else:
                self.failed_runs += 1
                logger.error(f"✗ Automation cycle completed with errors")
        
        except Exception as e:
            self.failed_runs += 1
            logger.error(f"✗ Automation cycle failed with exception: {e}", exc_info=True)
        
        # Calculate runtime
        job_duration = (datetime.now() - job_start).total_seconds()
        logger.info(f"Job duration: {job_duration:.2f} seconds")
        logger.info(f"Statistics: {self.successful_runs} successful, {self.failed_runs} failed, {self.total_runs} total")
        logger.info(f"Next run in {self.interval_minutes} minutes")
        logger.info("=" * 60)
    
    def start(self, run_immediately=True):
        """
        Start the scheduler.
        
        Args:
            run_immediately: If True, runs first cycle immediately before starting schedule
        """
        logger.info("=" * 60)
        logger.info("YouTube Horror Automation Scheduler Starting")
        logger.info(f"Interval: Every {self.interval_minutes} minutes ({self.interval_minutes/60:.2f} hours)")
        logger.info("=" * 60)
        
        # Run first cycle immediately if requested
        if run_immediately:
            logger.info("Running first automation cycle immediately...")
            self.job_wrapper()
        
        # Schedule recurring job
        self.scheduler.add_job(
            func=self.job_wrapper,
            trigger=IntervalTrigger(minutes=self.interval_minutes),
            id='youtube_automation_job',
            name='YouTube Horror Video Automation',
            replace_existing=True,
            max_instances=1  # Prevent overlapping runs
        )
        
        logger.info(f"Scheduler configured. Next run: {self.scheduler.get_jobs()[0].next_run_time}")
        
        try:
            # Start the scheduler (blocks forever)
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler shutdown requested")
            self.scheduler.shutdown()
            logger.info("Scheduler stopped gracefully")


# Entry point for Railway/production deployment
if __name__ == '__main__':
    # Get interval from environment variable or use default
    interval = int(os.getenv('AUTOMATION_INTERVAL_MINUTES', '288'))
    
    # Option to run immediately or wait for first interval
    run_immediately = os.getenv('RUN_IMMEDIATELY', 'true').lower() == 'true'
    
    # Create and start scheduler
    scheduler = AutomationScheduler(interval_minutes=interval)
    
    logger.info(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    logger.info(f"Run immediately: {run_immediately}")
    
    scheduler.start(run_immediately=run_immediately)
v
