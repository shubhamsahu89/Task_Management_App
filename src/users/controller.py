from fastapi import HTTPException,Depends,status,Request
from src.users.dtos import UserSchema,LoginSchema
from sqlalchemy.orm import Session
from src.users.models import UserModel
# from src.utils.db import get_db
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from src.utils.settings import settings
from datetime import datetime,timedelta,timezone
# from src.utils.db import get_db
password_hash = PasswordHash.recommended()
EXP_TIME=30
def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def register(body:UserSchema,db:Session):
    is_user=db.query(UserModel).filter(UserModel.username==body.username).first()
    if is_user:
        raise HTTPException(400,detail="User already exists")
    
    is_user=db.query(UserModel).filter(UserModel.email==body.email).first()
    if is_user:
        raise HTTPException(400,detail="Email already exists")
    

    hash_password=get_password_hash(body.password)

    new_user=UserModel(
        name=body.name,
        username=body.username,
        hash_password=hash_password,
        email=body.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def login(body:LoginSchema,db:Session):
    user=db.query(UserModel).filter(UserModel.username==body.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You entered wrong username")
    if not verify_password(body.password,user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect password")
    exp_time=datetime.now() + timedelta(minutes=settings.EXP_TIME)
    print(exp_time)
    token=jwt.encode({"id":user.id,"exp":exp_time.timestamp()},settings.SECRET_KEY,settings.ALGORITHM)

    return {"token":token}

#Token send 
def is_authenticated(request:Request,db:Session):
    try:
        token=request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authorized")
        token=token.split(" ")[-1]

        data =jwt.decode(token,settings.SECRET_KEY,settings.ALGORITHM)
        user_id=data.get("id")
        exp_time=int(data.get("exp"))
        current_time=datetime.now().timestamp()
        print(exp_time-current_time)

        # if current_time>exp_time:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authorized")
        
        user=db.query(UserModel).filter(UserModel.id==user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authorized")
        return user
    except InvalidTokenError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not authorized")