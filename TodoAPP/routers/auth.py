from typing import Annotated
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from ..database import SessionLocal
from ..models import *
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates

router = APIRouter(
     prefix='/auth',
     tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated= 'auto')

SECRET_KEY = 'fhjsbfjh477849hahiufpok7f'
ALGORITHM = 'HS256'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
templates = Jinja2Templates(directory='TodoAPP/templates')
##pages##
@router.get('/login-page')
def login_page(request:Request):
     return templates.TemplateResponse(request=request, name='login.html')

@router.get('/register-page')
def register_page(request:Request):
     return templates.TemplateResponse(request=request, name='register.html')
###Endpoints##


class new_user(BaseModel):
    email:str
    username:str
    first_name:str
    last_name:str
    password: str
    role: str
    phone_number:str
class Token (BaseModel):
     access_token:str
     token_type:str
    
def get_db(): # this function still stay the same in most projects, open and close the connection
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dependency = Annotated [Session, Depends(get_db)]

def authenticate (username, password, db):
     user = db.query(Users). filter(Users.username==username).first() # create an object
     if not user:
          raise HTTPException (status_code=401,  detail= 'Wrong username')
     if bcrypt_context.verify(password, user.hashed_password):
          return user
     else:
          raise HTTPException (status_code=401,  detail= 'Wrong password')

def create_jwt_token (data:dict, expires_delta: timedelta): # 3 steps, copy the data from verified user
     #update it with the expiration time
     # pass it to jwt and get a return token
     to_encode = data.copy()

     expire = datetime.now(timezone.utc) + expires_delta
     to_encode.update({"exp": expire})
     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
     return encoded_jwt

def get_current_user (token:str =Depends(oauth2_scheme)):
    try:
        payload = jwt.decode (token,SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get ('sub')
        user_id: int = payload.get ('id')
        user_role: str = payload.get ('user_role')
        if username is None or user_id is None:
            raise HTTPException (status_code= 401, detail= 'unuaturotized user')
        user_info = {'username':username, 'id': user_id, 'user_role': user_role}
        return user_info
    except JWTError:
         raise HTTPException(status_code=401, detail= 'Unauthorized user')

         
@router.post ('/create_user', status_code= status.HTTP_201_CREATED)
async def create_user(db:dependency, user: new_user):
    create_user_model = Users (
                     email = user.email,
                     username = user.username,
                     first_name = user.first_name,
                     last_name = user.last_name,
                     hashed_password = bcrypt_context.hash(user.password),
                     role = user.role,
                     is_active = True,
                     phone_number = user.phone_number
                     )
    
    db.add(create_user_model)
    db.commit()
    return db.query(Users).all()

@router.post('/login', response_model= Token) # the response type will be based on the Token class
async def login (input: Annotated[OAuth2PasswordRequestForm, Depends()], db: dependency):
        user = authenticate(input.username, input.password, db)
        if user is None:
             raise HTTPException (status_code= 401, detail='Autentication failed')
        user_data = {'sub': user.username, 'id':user.id, 'user_role': user.role}
        token = create_jwt_token(user_data, timedelta(minutes=15))
        return {'access_token': token,  'token_type': 'bearer'} # bearer mean the user is verified no aditional proof of identity is needed