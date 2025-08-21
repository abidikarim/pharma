from jose import jwt, JWTError, ExpiredSignatureError
from app.config import settings
from datetime import datetime, timedelta, timezone
from app import schemas, models
from fastapi import Cookie, HTTPException, Request, status,Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.schemas import UserRead
from app.routers.session import update_last_activity

ouath_schema=OAuth2PasswordBearer(tokenUrl="auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_min


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(pwd_plain: str, pwd_hashed: str):
    return pwd_context.verify(pwd_plain, pwd_hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def verif_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id = payload.get("id")
        token_data = schemas.TokenData(id=id)
        return token_data
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except Exception as e:
        raise credentials_exception


def get_current_user( request: Request, db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
    )
    access_token = request.cookies.get("access_token")
    token_data = verif_access_token(access_token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    update_last_activity(db,user.id)
    return UserRead.model_validate(user)