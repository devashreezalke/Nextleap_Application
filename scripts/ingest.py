import os
import sys
import logging

# Setup import path for src module resolving
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app.ingestion.pipeline import run_ingestion_pipeline

# Setup stdout logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("ingest")

if __name__ == "__main__":
    logger.info("Starting standalone data ingestion...")
    try:
        run_ingestion_pipeline()
        logger.info("Ingestion process completed.")
    except Exception as e:
        logger.error(f"Critical error during ingestion: {e}")
        sys.exit(1)
