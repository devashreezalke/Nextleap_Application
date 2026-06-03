import os
import logging
from app.config import settings
from app.ingestion.loader import load_raw_dataset
from app.ingestion.normalizer import normalize_dataset

logger = logging.getLogger(__name__)

def run_ingestion_pipeline():
    """
    Runs the complete ingestion pipeline:
    1. Downloads raw dataset from Hugging Face.
    2. Normalizes schema and cleans values.
    3. Saves result as a Parquet file.
    """
    logger.info("Starting ingestion pipeline execution...")
    
    # Load dataset
    raw_df = load_raw_dataset()
    
    # Normalize dataset
    processed_df = normalize_dataset(raw_df)
    
    # Ensure destination directories exist
    data_path = settings.DATA_PATH
    output_dir = os.path.dirname(data_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    # Write to Parquet format
    logger.info(f"Saving processed dataset to {data_path}...")
    processed_df.to_parquet(data_path, index=False)
    logger.info("Ingestion pipeline executed successfully!")
