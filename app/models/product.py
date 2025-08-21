from app.database import Base
from sqlalchemy import Column,Integer,Numeric,String,ForeignKey
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__="products"
    id=Column(Integer, primary_key=True)
    name=Column(String,nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    category_id=Column(Integer,ForeignKey("categories.id"),nullable=False)
    category = relationship("Category", back_populates="products")