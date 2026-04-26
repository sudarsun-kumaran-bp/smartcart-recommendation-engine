from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    price = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    tags = Column(String, nullable=False)  # stored as comma-separated string
