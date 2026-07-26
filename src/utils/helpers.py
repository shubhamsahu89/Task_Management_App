from fastapi import Request,HTTPException,status,Depends
from src.utils.settings import settings
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from src.users.models import UserModel 
from src.utils.db import get_db
from datetime import datetime,timedelta,timezone



#Token send 
def is_authenticated(request:Request,db:Session=Depends(get_db)):
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