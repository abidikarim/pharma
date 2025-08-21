from app.database import Base
from sqlalchemy import Column,Integer,func,ForeignKey,Enum,DateTime,String
from sqlalchemy.orm import relationship
from app.enums import OrderStatus

class Order(Base):
    __tablename__="orders"
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    buyer_phone = Column(Integer, nullable=False)
    buyer_address = Column(String, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, server_default=OrderStatus.Paid.value)
    created_on = Column(DateTime(timezone=True), server_default=func.now())
    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    session = relationship("Session", back_populates="orders")