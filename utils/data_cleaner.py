import re
import pandas as pd
from utils.logger import get_logger

logger = get_logger("DataCleaner")

class DataCleaner:
    def __init__(self, data: list):
        self.df = pd.DataFrame(data)
        logger.info(f"DataCleaner initialized with {len(self.df)} records")

    def remove_duplicates(self):
        before = len(self.df)
        self.df.drop_duplicates(subset=["url"], inplace=True)
        after = len(self.df)
        logger.info(f"Removed {before - after} duplicates. {after} records remaining")
        return self

    def normalize_whitespace(self):
        str_cols = self.df.select_dtypes(include="object").columns
        for col in str_cols:
            self.df[col] = self.df[col].apply(
                lambda x: " ".join(x.split()) if isinstance(x, str) else x
            )
        logger.info("Whitespace normalized")
        return self

    def convert_price(self):
        self.df["price"] = self.df["price"].apply(
            lambda x: float(re.sub(r'[^\d.]', '', str(x))) if x != "N/A" else None
        )
        for col in ["price_excl_tax", "price_incl_tax", "tax"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(
                    lambda x: float(re.sub(r'[^\d.]', '', str(x))) if x != "N/A" else None
                )
        logger.info("Prices converted to float")
        return self

    def convert_rating(self):
        self.df["rating"] = self.df["rating"].apply(
            lambda x: len(re.findall("⭐", str(x))) if x != "No rating" else 0
        )
        logger.info("Ratings converted to integers")
        return self

    def convert_reviews(self):
        self.df["num_reviews"] = pd.to_numeric(self.df["num_reviews"], errors="coerce").fillna(0).astype(int)
        logger.info("Number of reviews converted to integer")
        return self

    def clean(self):
        return (self
            .remove_duplicates()
            .normalize_whitespace()
            .convert_price()
            .convert_rating()
            .convert_reviews()
        )

    def to_json(self, filepath: str):
        self.df.to_json(filepath, orient="records", indent=2, force_ascii=False)
        logger.info(f"Clean data saved to {filepath}")

    def to_csv(self, filepath: str):
        self.df.to_csv(filepath, index=False, encoding="utf-8-sig")
        logger.info(f"Clean data saved to {filepath}")

    def summary(self):
        logger.info(f"Total records: {len(self.df)}")
        logger.info(f"Columns: {list(self.df.columns)}")
        logger.info(f"Price range: £{self.df['price'].min()} - £{self.df['price'].max()}")
        logger.info(f"Average rating: {self.df['rating'].mean():.2f}")
        return self.df.describe()
