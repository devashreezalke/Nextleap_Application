@echo off
echo ===================================================
echo Starting Mutual Fund FAQ Automated Ingestion...
echo ===================================================

echo The scheduler is running in the background.
echo It will automatically fetch, parse, chunk, and embed 
echo the mutual fund data every day at exactly 10:00 AM IST.

python -m backend.scheduler
