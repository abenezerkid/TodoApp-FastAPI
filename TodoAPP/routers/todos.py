#this page binds the model and detabase.py files and acomplish to create the database

from typing import Annotated
from pydantic import BaseModel, Field
from starlette import status
from fastapi import Depends, HTTPException, Path, Query,APIRouter, Request
from ..models import Todos, Users
from ..database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

router =APIRouter(
    prefix='/todos',
    tags=['todos']
)
templates = Jinja2Templates(directory='TodoAPP/templates')

def reverse_to_login():
    response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    return response


### page##
@router.get('/todo-page')
async def todo_page(request:Request, db:dependency):
    try:
        token = request.cookies.get('access_token')
        if token is None:
            return reverse_to_login()
        user = get_current_user(token=token)
        if user.get('user_role')=='admin':
            todos = db.query(Todos).all()
        else: todos = db.query(Todos).filter(Todos.owner_id==user.get('id')).all()
        name = db.query(Users).filter(Users.id==user.get('id')).first()
        name_value=name.first_name
        return templates.TemplateResponse(request=request, name='todo.html', context={'todos':todos, 'name':name_value,'user':user })
    except Exception:
        return reverse_to_login()
    

@router.get('/add-todo')
async def add_todo_page(request:Request): 
    token = request.cookies.get('access_token')
    user =get_current_user(token)
    if user is None:
        return reverse_to_login()
    return templates.TemplateResponse(request=request, name='add-todo.html', context={"user":user})

@router.get('/edit-todo/{todo_id}')
async def get_update_page(request:Request, todo_id :str, db:dependency):
    token = request.cookies.get('access_token')
    user = get_current_user(token=token)
    if user is None:
        return reverse_to_login()
    
    todo= db.query(Todos).filter(Todos.id ==todo_id).first()
    if todo is None:
        return reverse_to_login()
    return templates.TemplateResponse(request=request, name='edit-todo.html', context={'todo':todo, 'todoId':todo_id})

@router.post('/complete/{todo_id}')
def update_complete(request:Request, todo_id:int, db:dependency):
    token = request.cookies.get('access_token')
    user = get_current_user(token=token)
    if user is None:
        return reverse_to_login()
    if user.get('user_role')=='admin':
        todo = db.query(Todos).filter(Todos.id==todo_id).first()
    else:
        todo = db.query(Todos).filter(Todos.id==todo_id, user.get('id')==Todos.owner_id).first()
    if todo is None:
        return RedirectResponse(url='/todos/todo-page', status_code= status.HTTP_302_FOUND)
    todo.complete= True
    db.commit()

    return RedirectResponse(
        url='/todos/todo-page',
        status_code=status.HTTP_302_FOUND
    )

@router.post('/complete_undo/{todo_id}')
async def undo_compltee(request:Request, todo_id:int, db:dependency):
    token = request.cookies.get("access_token")
    user = get_current_user(token=token)
    if user is None:
        return reverse_to_login()
    if user.get('user_role')=='admin':
        todo= db.query(Todos).filter(Todos.id==todo_id).first()
        todo.complete= False
        db.commit()
        return RedirectResponse(url='/todos/todo-page', status_code= status.HTTP_302_FOUND)
    else:
        todo = db.query(Todos).filter(Todos.id == todo_id, user.get('id')==Todos.owner_id).first()
        todo.complete = False
        db.commit()
        return RedirectResponse(url='/todos/todo-page', status_code= status.HTTP_302_FOUND)

###endpoints##

def get_db(): # this function still stay the same in most projects, open and close the connection
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dependency = Annotated [Session, Depends(get_db)]
jwt_dependency = Annotated[dict, Depends(get_current_user)]

class validation (BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field (gt=0, lt=6)
    complete: bool

@router.get('/', status_code= status.HTTP_200_OK)
async def list_todo (user: jwt_dependency, db: dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='user is not authenticated')
    Item = db.query(Todos).filter(Todos.owner_id==user.get ('id')).all()
    return Item

@router.get('/{todo_id}', status_code= status.HTTP_200_OK)
async def find_by_id (user: jwt_dependency,db:dependency, todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='user is not authenticated')
    item = db.query(Todos).filter(user.get('id')==Todos.owner_id, Todos.id == todo_id).first()
    if item is not None:
        return item
    else:
        raise HTTPException(status_code=404, detail= 'Your items is not found')
    
@router.get ('/filter_priority', status_code= status.HTTP_200_OK)
async def find_priority (user: jwt_dependency,db:dependency, priority:int = Query(gt=0,lt=6)):
    if user is None:
        raise HTTPException(status_code=401, detail='user is not authenticated')
    
    item = db.query(Todos). filter(user.get('id')==Todos.owner_id,priority == Todos.priority).all()

    if len(item)==0:
        raise HTTPException(status_code=404, detail='The item is not found')
    else:
        return item
    
@router.post('/add_todo', status_code= status.HTTP_201_CREATED)
async def adding_todo(user: jwt_dependency, db: dependency, new_todo: validation):
    if user is None:
        raise HTTPException(status_code= 401, detail= 'Anunthenticated User')
    new_item = Todos(**new_todo.model_dump(),owner_id = user.get('id'))

    db.add(new_item)
    db.commit()
    return new_item

@router.put('/update_todo/{todoId}', status_code= status.HTTP_204_NO_CONTENT)
async def update_record (user: jwt_dependency, db: dependency, update:validation, todoId:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code= 401, detail= 'Anunthenticated User')
    
    if user.get('user_role')=='admin':
        find_item = db.query(Todos).filter(Todos.id==todoId).first()
    else:
        find_item = db.query(Todos).filter(Todos.id==todoId, user.get('id')==Todos.owner_id).first()
    if find_item is not None:
        find_item.title=update.title
        find_item.description =update.description
        find_item.priority= update.priority
        find_item.complete = update.complete
        db.add(find_item)
        db.commit()
        db.refresh(find_item)
    else:
        raise HTTPException(status_code=404, detail= 'Item not found')

@router.delete('/delete_todo/{delete_id}', status_code= status.HTTP_204_NO_CONTENT)
async def delete (user: jwt_dependency, db:dependency, delete_id:int = Path(gt=0)):
    delete_item = db.query(Todos).filter(Todos.id == delete_id, user.get ('id')==Todos.owner_id).first()
    if delete_item is None:
        raise HTTPException(status_code=404, detail='Item not found')
    db.delete(delete_item)
    db.commit()