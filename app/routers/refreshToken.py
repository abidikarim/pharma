from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.config import settings
from app.models import RefreshToken, BlacklistToken
from app.database import get_db
from app.schemas import OurBaseModelOut
from app.oauth2 import create_access_token
from datetime import datetime, timedelta, timezone
import hashlib
import uuid

router = APIRouter(prefix="/refresh", tags=["Refresh Token"])

@router.post("/")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return OurBaseModelOut(status=401, message="Refresh token not found")

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

        if not db_token:
            return OurBaseModelOut(status=401, message="Invalid refresh token")

        if db_token.expires_at < datetime.now(timezone.utc):
            return OurBaseModelOut(status=401, message="Refresh token expired")

        if db.query(BlacklistToken).filter(BlacklistToken.token_hash == token_hash).first():
            return OurBaseModelOut(status=401, message="Refresh token is blacklisted")

        db.add(BlacklistToken(token_hash=db_token.token_hash, session_id=db_token.session_id, expires_at=db_token.expires_at))
        db.delete(db_token)

        new_refresh_token = create_refresh_token(db, db_token.session_id)
        access_token = create_access_token({"id": db_token.session.user.id, "role": db_token.session.user.role.value})

        response.set_cookie(
           key="refresh_token",
           value=new_refresh_token, 
           httponly=True, 
           secure=False,  
           samesite="lax",
           max_age=settings.refresh_token_expire_day * 24 * 60 * 60
        )
        response.set_cookie(
           key="access_token",
           value=access_token, 
           httponly=True, 
           secure=False,  
           samesite="lax",
           max_age=settings.refresh_token_expire_day * 60
        )

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return OurBaseModelOut(status=500, message="An error occurred while refreshing token")


def create_refresh_token(db:Session,session_id:int):
    try:
        expired_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_day)
        token = str(uuid.uuid4())
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        refresh_token = RefreshToken(token_hash=token_hash, session_id=session_id,expires_at=expired_at)
        db.add(refresh_token)
        db.flush()
        return token
    except Exception as e:
        return None
    

def blacklisted_refresh_tokens(db:Session,session_id:int):
    try:
        refresh_tokens = db.query(RefreshToken).filter(RefreshToken.session_id == session_id).all()
        if refresh_tokens:
             db.bulk_save_objects([BlacklistToken(token_hash=t.token_hash, session_id=t.session_id, expires_at=t.expires_at) for t in refresh_tokens])
             db.query(RefreshToken).filter_by(session_id=session_id).delete(synchronize_session=False)
        db.flush()
        return True
    except Exception as e:
        return False