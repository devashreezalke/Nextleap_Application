import logging
from datasets import load_dataset
import pandas as pd

logger = logging.getLogger(__name__)

def load_raw_dataset(dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation") -> pd.DataFrame:
    """
    Downloads the dataset from Hugging Face and returns it as a Pandas DataFrame.
    """
    logger.info(f"Downloading dataset '{dataset_name}' from Hugging Face...")
    try:
        dataset = load_dataset(dataset_name)
        
        # Access the first available split
        if not dataset:
            raise ValueError("Dataset fetched from Hugging Face is empty.")
            
        split_name = list(dataset.keys())[0]
        df = dataset[split_name].to_pandas()
        
        logger.info(f"Successfully loaded raw dataset. Rows: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"Error loading dataset from Hugging Face: {e}")
        raise
