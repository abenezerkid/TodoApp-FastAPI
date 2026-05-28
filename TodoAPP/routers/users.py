#jwt
#db.user table
from typing import Annotated
from pydantic import BaseModel, Field
from starlette import status
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Path, Query,APIRouter 
from ..models import Todos, Users
from ..database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

router =APIRouter(
    prefix='/users',
    tags=['users']
)
class pw_change (BaseModel):
    Old_password: str
    new_password: str

def get_db(): # this function still stay the same in most projects, open and close the connection
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dependency = Annotated [Session, Depends(get_db)]
jwt_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated= 'auto')

@router.get ('/current_user_info', status_code= status.HTTP_200_OK)
async def current_user_info(user:jwt_dependency,db:dependency):
    if user is None:
        raise HTTPException (status_code= 401, detail='Autentication failed')
    
    return db.query(Users).filter(user.get ('id')==Users.id).first()

@router.put ('/change_pw', status_code= status.HTTP_204_NO_CONTENT)
async def change_pss_wd (pw_info:pw_change, user:jwt_dependency, db:dependency):
    if user is None:
        raise HTTPException (status_code= 401, detail='Autentication failed')

    user_obj = db.query(Users).filter(user.get ('id')== Users.id).first()
    if not bcrypt_context.verify(pw_info.Old_password, user_obj.hashed_password):
          raise HTTPException (status_code= 401, detail='wrong password')

    
    user_obj.hashed_password = bcrypt_context.hash (pw_info.new_password)
    db.commit()
@router.put('/update_phone_number/{phone_num}', status_code= status.HTTP_204_NO_CONTENT)
async def change_phone(phone_num:str, user:jwt_dependency, db:dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='An authorized use')
    user_data = db.query(Users).filter(user.get('id')==Users.id).first()
    user_data.phone_number = phone_num
    db.commit()
    return db.query(Users).filter(user.get('id')==Users.id).first()

@router.delete('/delete_account/{delete_username}', status_code= status.HTTP_204_NO_CONTENT)
async def delete_account(delete_username:str, db:dependency, user:jwt_dependency):
    if user is None:
        raise HTTPException(status_code= 401, detail="Unauthorized User")
    delete_user = db.query(Users).filter(Users.username == delete_username).first()
    if delete_user is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail='user is not found')
    db.delete(delete_user)
    db.commit()