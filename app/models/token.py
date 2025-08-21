from app.database import Base
from sqlalchemy import Column,String,Integer,ForeignKey,TIMESTAMP,func,Boolean,text


class Token(Base):
    __tablename__="tokens"
    id = Column(Integer,primary_key=True,nullable=False)
    token=Column(String,nullable=False)
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    isUsed=Column(Boolean,nullable=False,server_default=text('false'))
    created_at = Column(TIMESTAMP, server_default=func.now())