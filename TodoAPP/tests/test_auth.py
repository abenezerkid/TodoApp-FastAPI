from .utils import *
from ..routers.auth import get_db
from starlette import status
from ..routers.auth import authenticate, create_jwt_token, ALGORITHM, SECRET_KEY, get_current_user
from datetime import timedelta, datetime, timezone
from jose import jwt
from fastapi import HTTPException


app.dependency_overrides[get_db] = override_get_db


def test_auth_create_acct (add_user):
    jason_data ={'email' :'Tesr',
                 'username' : 'Test',
                 'first_name' : 'Test',
                 'last_name' : 'Test',
                 'password' : 'bcrypt',
                 'role' : 'admin',
                 'phone_number' : 'test'}
    
    response = client.post('/auth/create_user', json= jason_data)
    if response.status_code == 422:
        print(response.json())
    assert response.status_code == status.HTTP_201_CREATED


def test_autenticate(add_user):
    db_test = TestSessionLocal()
    user= authenticate('user.username','password',db_test)
    assert user.username == 'user.username'

def test_create_jwt ():
    user_data = {'sub': "test", 'id':"1", 'user_role': "admin"}
    time_pass = timedelta(minutes=15)
    token =  create_jwt_token(user_data,time_pass)
    payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get('sub')==user_data.get('sub')
    assert payload.get('id')==user_data.get('id')


def test_get_current_user():
    user_data = {'sub': "test", 'id':"1", 'user_role': "admin"}
    time_pass = datetime.now(timezone.utc) + timedelta(minutes=15)
    user_data.update ({"exp":time_pass})
    token = jwt.encode(user_data,SECRET_KEY, algorithm= ALGORITHM)
    out_put = get_current_user(token)
    assert out_put.get('username')== user_data.get ('sub')

def test_get_current_user_missing_payload():
    user_data = {'user_role': "admin"}
    token = jwt.encode(user_data,SECRET_KEY, algorithm= ALGORITHM)
    with pytest.raises(HTTPException) as exept:
        out_put = get_current_user(token)
    assert exept.value.status_code== 401
    assert exept.value.detail =='unuaturotized user'


def test_login (add_user):
    jsond_data= {'username': 'user.username', 'password':'password', "scope":'', 'grant_type':'password'}
    response = client.post('/auth/login', data= jsond_data)
    print (response.json())
    assert response.json()['token_type']== 'bearer'