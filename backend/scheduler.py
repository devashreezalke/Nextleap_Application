import schedule
import time
import subprocess
import pytz
from datetime import datetime
import logging
import sys
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("IngestionScheduler")

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent

def run_ingestion_pipeline():
    """Runs the full data ingestion pipeline sequentially."""
    logger.info("Starting automated ingestion pipeline...")
    
    scripts = [
        "ingestion/fetch.py",
        "ingestion/parse.py",
        "ingestion/chunker.py",
        "ingestion/embed.py"
    ]
    
    for script in scripts:
        logger.info(f"Running {script}...")
        try:
            # Run the script using the same python executable
            result = subprocess.run(
                [sys.executable, script], 
                cwd=str(PROJECT_ROOT),
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Successfully completed {script}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Pipeline failed at {script}!")
            logger.error(f"Error output:\n{e.stderr}")
            return # Stop the pipeline if one step fails
            
    logger.info("Automated ingestion pipeline completed successfully!")

def is_time_ist(target_hour, target_minute):
    """Check if the current IST time matches the target time."""
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    return now_ist.hour == target_hour and now_ist.minute == target_minute

def job():
    """The job to run when the schedule triggers."""
    run_ingestion_pipeline()

def start_scheduler():
    logger.info("Scheduler started. Waiting for 10:00 AM IST daily...")
    
    # We use a custom loop to check IST time precisely
    # since `schedule` uses local system time by default.
    while True:
        # Check if it is exactly 10:00 AM IST
        if is_time_ist(10, 0):
            job()
            # Sleep for 61 seconds to ensure it doesn't trigger multiple times in the same minute
            time.sleep(61)
        else:
            # Check every 30 seconds
            time.sleep(30)

if __name__ == "__main__":
    start_scheduler()
