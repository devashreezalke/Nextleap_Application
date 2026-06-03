import os
import logging
import pandas as pd
from typing import List, Optional
from app.config import settings
from app.models.schemas import Restaurant

logger = logging.getLogger(__name__)

class RestaurantRepository:
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or settings.DATA_PATH
        self._df: pd.DataFrame = pd.DataFrame()
        self.load_data()

    def load_data(self):
        """
        Loads the Parquet file into an in-memory Pandas DataFrame.
        """
        logger.info(f"Loading restaurant dataset from {self.data_path}...")
        if not os.path.exists(self.data_path):
            logger.warning(f"Dataset path {self.data_path} does not exist. Repository initialized empty.")
            self._df = pd.DataFrame(columns=["id", "name", "location", "cuisines", "rating", "estimated_cost", "budget_band", "votes", "address"])
            return

        try:
            self._df = pd.read_parquet(self.data_path)
            logger.info(f"Successfully loaded {len(self._df)} restaurants in-memory.")
        except Exception as e:
            logger.error(f"Error loading Parquet file: {e}")
            raise

    def get_df(self) -> pd.DataFrame:
        """
        Returns the raw internal DataFrame.
        """
        return self._df

    def get_all(self) -> List[Restaurant]:
        """
        Returns all restaurants as Pydantic models.
        """
        return [Restaurant(**row) for row in self._df.to_dict(orient="records")]

    def get_by_id(self, restaurant_id: str) -> Optional[Restaurant]:
        """
        Resolves a single restaurant by its unique ID.
        """
        match = self._df[self._df["id"] == restaurant_id]
        if match.empty:
            return None
        row_dict = match.iloc[0].to_dict()
        # Convert numpy lists to standard Python lists
        if isinstance(row_dict.get("cuisines"), (list, tuple, pd.Series)):
            row_dict["cuisines"] = list(row_dict["cuisines"])
        return Restaurant(**row_dict)

    def get_by_ids(self, ids: List[str]) -> List[Restaurant]:
        """
        Resolves multiple restaurants by their IDs, maintaining the order of the ids parameter.
        """
        if not ids:
            return []
        
        # Load match rows
        matches = self._df[self._df["id"].isin(ids)]
        results_map = {}
        for _, row in matches.iterrows():
            row_dict = row.to_dict()
            if isinstance(row_dict.get("cuisines"), (list, tuple, pd.Series)):
                row_dict["cuisines"] = list(row_dict["cuisines"])
            results_map[row_dict["id"]] = Restaurant(**row_dict)
            
        # Return ordered matches
        return [results_map[rid] for rid in ids if rid in results_map]

    def get_locations(self) -> List[str]:
        """
        Returns a sorted list of unique locations.
        """
        if self._df.empty or "location" not in self._df.columns:
            return []
        return sorted(self._df["location"].dropna().unique().tolist())

    def get_cuisines(self) -> List[str]:
        """
        Returns a sorted list of unique cuisines.
        """
        if self._df.empty or "cuisines" not in self._df.columns:
            return []
        
        cuisines_set = set()
        for c_list in self._df["cuisines"].dropna():
            if isinstance(c_list, (list, tuple, pd.Series)):
                for c in c_list:
                    cuisines_set.add(c)
            elif isinstance(c_list, str):
                cuisines_set.add(c_list)
                
        return sorted(list(cuisines_set))
