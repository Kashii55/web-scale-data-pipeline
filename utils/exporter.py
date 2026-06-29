import json
import csv
import os
import pandas as pd
from utils.logger import get_logger

logger = get_logger("Exporter")

class Exporter:
    def __init__(self, data: list, output_dir: str = "output"):
        self.data = data
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Exporter initialized with {len(data)} records")

    def to_json(self, filename: str = "books.json"):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON exported: {filepath} ({len(self.data)} records)")
        return filepath

    def to_csv(self, filename: str = "books.csv"):
        filepath = os.path.join(self.output_dir, filename)
        if not self.data:
            logger.warning("No data to export")
            return
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)
        logger.info(f"CSV exported: {filepath} ({len(self.data)} records)")
        return filepath

    def to_excel(self, filename: str = "books.xlsx"):
        filepath = os.path.join(self.output_dir, filename)
        df = pd.DataFrame(self.data)
        df.to_excel(filepath, index=False, engine="openpyxl")
        logger.info(f"Excel exported: {filepath} ({len(self.data)} records)")
        return filepath

    def export_all(self, base_filename: str = "books"):
        json_path = self.to_json(f"{base_filename}.json")
        csv_path = self.to_csv(f"{base_filename}.csv")
        excel_path = self.to_excel(f"{base_filename}.xlsx")
        logger.info("All formats exported successfully")
        return {
            "json": json_path,
            "csv": csv_path,
            "excel": excel_path
        }
