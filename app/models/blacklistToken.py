from app.database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,TIMESTAMP,func,DateTime
from sqlalchemy.orm import relationship

class BlacklistToken(Base):
    __tablename__ ="blacklist_tokens"
    id = Column(Integer, primary_key=True)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    session = relationship("Session", back_populates="blacklist_tokens")