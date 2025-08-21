from fastapi import APIRouter,Depends,Request,Response
from app.schemas import OurBaseModelOut, AccessToken,MailData,ForgetPassword,ConfirmData, UserRead
from app.oauth2 import create_access_token,verify_password,hash_password
from app.database import get_db
from sqlalchemy.orm import Session as DbSession
from app.models import User,Token,Session
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import datetime
from app.utils import send_mail
import uuid
from app.routers.session import create_session
from app.routers.refreshToken import create_refresh_token, blacklisted_refresh_tokens
from app.config import settings
from app.oauth2 import get_current_user

router = APIRouter(prefix="/auth", tags=["Authenticate"])


@router.post("/login")
def login(request: Request, response: Response, user_credentials: OAuth2PasswordRequestForm = Depends(), db:DbSession = Depends(get_db)):
    try:
       user = db.query(User).filter(User.email == user_credentials.username).first()

       if not user:
           return OurBaseModelOut(status=404,message="User with is email not found")
       
       if not verify_password(user_credentials.password,user.password):
            return OurBaseModelOut(status=400,message="Wrong password")
       
       active_session = db.query(Session).filter(Session.user_id == user.id, Session.is_active == True).first()
       if active_session:
           blacklisted_refresh_tokens(db, active_session.id)
           active_session.is_active = False
        
       access_token = create_access_token({"id":user.id,"role":user.role.value})
       new_session = create_session(db, user.id,request)
       refresh_token = create_refresh_token(db, new_session.id)

       response.set_cookie(
           key="refresh_token", value=refresh_token, 
           httponly=True, secure=True,  
           max_age=settings.refresh_token_expire_day * 24 * 60 * 60
        )
       
       db.commit()
       return AccessToken(token_type="Bearer", access_token=access_token,status=200, message="Login successfuly")
    except Exception as error:
        db.rollback()
        return OurBaseModelOut(status=400, message="Login failed. Please try again.")

@router.post("/forget_password")
async def forget_password(data:ForgetPassword,db:DbSession=Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            return OurBaseModelOut(status=404,message="User with is email not found")
        
        token = Token(token=uuid.uuid4(),user_id=user.id)
        db.add(token)

        await send_mail(MailData(
            emails=[user.email],
            body={"name": f"{user.first_name} {user.last_name}","code":token.token},
            template="reset_password.html",
            subject="Reset Password",
        )) 

        db.commit()
        return OurBaseModelOut(status=200,message="Email send with successfully")
    except Exception as error:
        db.rollback()
        return OurBaseModelOut(status=400,message="Email send failed. Please try again.")  
    

@router.patch("/confirm_account")
def confirm_account(confirm_data:ConfirmData,db:DbSession=Depends(get_db)):
    try:
        if confirm_data.password != confirm_data.confirm_password:
            return OurBaseModelOut(status=400,message="Password and confirm password must match.")
        
        token = db.query(Token).filter(Token.token == confirm_data.code).first()
        if token.isUsed:
            return OurBaseModelOut(status=400,message="Link already used")
        
        if (datetime.now() - token.created_at.replace(tzinfo=None)).days > 1:
            return OurBaseModelOut(status=400,message="Link expired")
        
        db.query(User).filter(User.id == token.user_id).update({User.password:hash_password(confirm_data.password)})
        db.query(Token).filter(Token.id == token.id).update({Token.isUsed:True})
        db.commit()
        return OurBaseModelOut(status=200,message="Account confirmed successfuly")
    except Exception as error:
        return OurBaseModelOut(status=400,message="Confirm account failed. Please try again.")
    
@router.patch("/reset_password")
def reset_password(confirm_data:ConfirmData, db:DbSession=Depends(get_db)):
    try:
        if confirm_data.password != confirm_data.confirm_password:
            return OurBaseModelOut(status=400,message="Password and confirm password must match.")
        
        token = db.query(Token).filter(Token.token == confirm_data.code).first()
        if token.isUsed:
            return OurBaseModelOut(status=400,message="Link already used")
        
        if (datetime.now() - token.created_at.replace(tzinfo=None)).days > 1:
            return OurBaseModelOut(status=400,message="Link expired")
        
        db.query(User).filter(User.id == token.user_id).update({User.password:hash_password(confirm_data.password)})
        db.query(Token).filter(Token.id == token.id).update({Token.isUsed:True})
        db.commit()
        return OurBaseModelOut(status=200,message="Password updated successfuly")
    except Exception as error:
        return OurBaseModelOut(status=400,message="Update password failed. Please try again.")
    
@router.get("/logout")
def logout(response: Response, db: DbSession = Depends(get_db), current_user: UserRead  = Depends(get_current_user)):
    try:
        active_session = db.query(Session).filter(Session.user_id == current_user.id, Session.is_active == True).first()
        if active_session:
            blacklisted_refresh_tokens(db, active_session.id)
            active_session.is_active = False
            db.commit()
        
        response.delete_cookie("refresh_token")
        return OurBaseModelOut(status=200, message="Logout successfuly")
    except Exception as error:
        return OurBaseModelOut(status=400, message="Logout failed. Please try again.")