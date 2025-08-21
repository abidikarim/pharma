from app.database import Base
from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__="categories"
    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False)
    description=Column(String,nullable=False)
    image_link=Column(String,nullable=True)
    public_id=Column(String,nullable=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    products = relationship("Product", back_populates="category")
    user=relationship("User",back_populates="categories")