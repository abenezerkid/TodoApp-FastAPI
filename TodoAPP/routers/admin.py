from typing import Annotated
from pydantic import BaseModel, Field
from starlette import status
from fastapi import Depends, HTTPException, Path, Query,APIRouter 
from ..models import Todos, Users
from ..database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

# username: test
#pw: test
# to test the admin routes 

router =APIRouter(prefix='/admin',
     tags=['admin'])

def get_db(): # this function still stay the same in most projects, open and close the connection
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dependency = Annotated [Session, Depends(get_db)]
jwt_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/list_all_users')
async def list_all_users(db:dependency, user:jwt_dependency):
    if user is None or user.get("user_role")!='admin':
        raise HTTPException(status_code=401, detail="Unauthorized User")
    user_list = db.query(Users).all()
    return user_list

@router.get('/lis_all', status_code=status.HTTP_200_OK)
async def admin_list_all (user:jwt_dependency, db: dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException (status_code=401, detail='Unauthorized User')
    all_todos= db.query(Todos).all()
    return all_todos


@router.get ('/{todo_id}')
async def get_by_id(user:jwt_dependency, todo_id:int, db:dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException (status_code=401, detail='Unauthorized User')
    item = db.query(Todos).filter(todo_id==Todos.id).first()
    return item

@router.delete('/delete/{delete_id}', status_code= status.HTTP_204_NO_CONTENT)
async def delete_todo (user:jwt_dependency, delete_id:int, db:dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException (status_code=401, detail='Unauthorized User')
    item = db.query(Todos).filter(delete_id==Todos.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail= 'Todo is not found')
    db.delete(item)
    db.commit ()
    return db.query(Todos).all()
    
@router.delete('/delete_account/{delete_user}')
async def delete_account(delete_user:str, db:dependency, user:jwt_dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code= 401, detail="Unauthorized User")
    delete_user_name = db.query(Users).filter(Users.username == delete_user).first()
    if delete_user_name is None:
        raise HTTPException(status_code= 404, detail="user is not found")
    db.delete(delete_user_name)
    db.commit()
    return {'message': f'user {delete_user} account is deleted'}