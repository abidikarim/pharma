from app.database import Base
from sqlalchemy import Column, String, Integer, TIMESTAMP, func, ForeignKey


class Error(Base):
    __tablename__ = "errors"
    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    text = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())