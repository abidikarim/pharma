from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import User,Token
from app.schemas import UserCreate, UserRead, UserUpdate, OurBaseModelOut,MailData
from app.database import get_db
from app.oauth2 import hash_password, get_current_user
from app.utils import send_mail
import uuid
from app.routers.error import get_error_detail,add_error

router = APIRouter(prefix="/users", tags=["users"])

error_keys = {
    "users_pkey": {"message": "User not found", "status": 404},
    "ix_users_email": {"message": "Email already exists", "status": 400}
}

@router.post("/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=hash_password(user.password),
        )

        db.add(db_user)
        db.flush()
        db_token = Token(token=uuid.uuid4(),user_id=db_user.id)
        db.add(db_token)

        await send_mail(MailData(
            emails=[db_user.email],
            body={"name": f"{db_user.first_name} {db_user.last_name}","code":db_token.token},
            template="confirm_account.html",
            subject="Confirm Account",
        ))   

        db.commit()
        return OurBaseModelOut(status=201, message="User created successfully")

    except Exception as e:
        db.rollback()
        add_error(str(e),db)
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])

@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
         return OurBaseModelOut(status=404, message="User not found")
        
        return UserRead.model_validate(user)
    
    except Exception as e:
        return OurBaseModelOut(status=400, message="An error occurred while fetching user details")

@router.put("/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return OurBaseModelOut(status=404, message="User not found")
        
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)

        return OurBaseModelOut(status=200, message="User updated successfully")
    
    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        deleted_row = db.query(User).filter(User.id == user_id).delete()

        if not deleted_row:
            return OurBaseModelOut(status=404,message="User not found")
        
        db.commit()
        return OurBaseModelOut(status=200, message="User deleted successfully")
    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])