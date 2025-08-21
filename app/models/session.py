from app.database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,TIMESTAMP,func,Text,Boolean,DateTime
from sqlalchemy.orm import relationship

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    last_activity_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    refresh_tokens = relationship("RefreshToken", back_populates="session", cascade="all, delete-orphan")
    blacklist_tokens = relationship("BlacklistToken", back_populates="session", cascade="all")
    user = relationship("User", back_populates="sessions")
    orders = relationship("Order", back_populates="session", cascade="all, delete-orphan")
