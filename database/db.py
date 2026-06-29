from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Book
from utils.logger import get_logger
import yaml

logger = get_logger("Database")

class Database:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        db = config["database"]
        self.url = f"postgresql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['name']}"
        self.engine = create_engine(self.url)
        self.Session = sessionmaker(bind=self.engine)
        logger.info("Database connection established")

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        logger.info("Tables created successfully")

    def insert_books(self, data: list):
        session = self.Session()
        inserted = 0
        skipped = 0
        try:
            for record in data:
                existing = session.query(Book).filter_by(upc=record.get("upc")).first()
                if existing:
                    skipped += 1
                    continue
                book = Book(
                    title=record.get("title"),
                    price=record.get("price"),
                    availability=record.get("availability"),
                    rating=record.get("rating"),
                    description=record.get("description"),
                    upc=record.get("upc"),
                    product_type=record.get("product_type"),
                    price_excl_tax=record.get("price_excl_tax"),
                    price_incl_tax=record.get("price_incl_tax"),
                    tax=record.get("tax"),
                    num_reviews=record.get("num_reviews"),
                    image_url=record.get("image_url"),
                    url=record.get("url")
                )
                session.add(book)
                inserted += 1
            session.commit()
            logger.info(f"Inserted {inserted} books, skipped {skipped} duplicates")
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    def get_all_books(self):
        session = self.Session()
        try:
            books = session.query(Book).all()
            return books
        finally:
            session.close()

    def close(self):
        self.engine.dispose()
        logger.info("Database connection closed")
