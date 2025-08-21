from app.models import Session
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import desc
from fastapi import Request
from app.utils import get_location_from_ip
import json
from app.schemas import SessionBase
from datetime import datetime,timezone

def create_session(db: DbSession, user_id: int, request: Request):
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        location = get_location_from_ip(ip_address)
        location_str = json.dumps(location) if location else None
        new_session = Session(user_id=user_id, ip_address=ip_address, user_agent=user_agent, location=location_str)
        db.add(new_session)
        db.flush()
        return SessionBase.model_validate(new_session)
    except Exception as e:
        return None
    

def get_active_session(db: DbSession, user_id: int):
    try:
        active_session = db.query(Session).filter(Session.user_id == user_id, Session.is_active == True).first()
        if not active_session:
            return None
        return SessionBase.model_validate(active_session)
    except Exception as e:
        return None

def update_last_activity(db: DbSession, user_id: int):
    try:
        session_db = db.query(Session).filter(Session.user_id == user_id).order_by(desc(Session.created_at)).first()
        session_db.last_activity_at = datetime.now(timezone.utc)
        db.commit()
        return True
    except Exception as e:
        return None