from app.database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,TIMESTAMP,DateTime,func
from sqlalchemy.orm import relationship

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    session_id = Column(Integer, ForeignKey("sessions.id",ondelete="CASCADE"))
    session = relationship("Session", back_populates="refresh_tokens")