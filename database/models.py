from sqlalchemy import Column, String, Float, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    price = Column(Float)
    availability = Column(String(100))
    rating = Column(Integer)
    description = Column(Text)
    upc = Column(String(100), unique=True)
    product_type = Column(String(100))
    price_excl_tax = Column(Float)
    price_incl_tax = Column(Float)
    tax = Column(Float)
    num_reviews = Column(Integer)
    image_url = Column(String(500))
    url = Column(String(500), unique=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Book(title={self.title}, price={self.price})>"
