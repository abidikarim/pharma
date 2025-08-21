from app.database import Base
from sqlalchemy import Column,String,Integer,DateTime,func,Enum
from app.enums import Role,AccountStatus
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    first_name=Column(String,nullable=False)
    last_name=Column(String,nullable=False)
    email=Column(String,unique=True,nullable=False,index=True)
    password=Column(String,nullable=False)
    role=Column(Enum(Role),nullable=False,server_default=Role.Buyer.value)
    status=Column(Enum(AccountStatus),nullable=False,server_default=AccountStatus.Inactive.value)
    created_on=Column(DateTime(timezone=True),server_default=func.now())
    orders = relationship("Order", back_populates="buyer")
    categories = relationship("Category", back_populates="user")
    sessions = relationship("Session", back_populates="user")
