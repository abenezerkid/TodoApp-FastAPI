from sqlalchemy import create_engine, text, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # this is new importing the sqlalchemy pool
from fastapi import status
from ..routers.todos import get_current_user, get_db
from fastapi.testclient import TestClient
from ..database import Base
from ..main import app
from ..models import Todos
import pytest

Test_SQLALCHEMY_DATABASE_URL='sqlite:///./testbd.bd' 
engine = create_engine(Test_SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False},
                        poolclass= StaticPool) # new change about poolclass
TestSessionLocal = sessionmaker(autocommit =False, autoflush= False, bind =engine)

Base.metadata.create_all(bind=engine) # crate all the tables from base, and model is a child of base class from database

def override_get_db ():
    db = TestSessionLocal()
    try: 
        yield db #this is actually interesting makes the database running till the route completed,
        #once it's done pass it to db.cloe  close the session 
    finally:
        db.close()

def override_ger_currenet_user():
    return {'username':'test', 'id':1 , 'user_role':'admin'}

app.dependency_overrides[get_db]= override_get_db #overriding existing get_db and get_current_db from todos when we run the test
app.dependency_overrides[get_current_user]= override_ger_currenet_user

 #the way how the computer knows is the app is chnaged Because TestClient(app) uses the app after overrides were registered.
client = TestClient(app) # this is how we force it to take this. new test new db and jwt dependency


@pytest.fixture
def add_todo ():
    todo_add = Todos(id = 1, title ='Test', description ='Test', priority = 3, owner_id = 1)
    db = TestSessionLocal ()
    db.add(todo_add)
    db.commit()
    yield db

    item = db.query(Todos).all()
    for each in item:
        db.delete(each)
    db.commit()
    db.close()
    #with engine.connect() as connection:
        #connection.execute(text("DELETE FROM todos"))
        #connection.commit()


def test_todos_func (add_todo):
    response = client.get('/todo')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() ==[{"id":1,"title":"Test","description":"Test","priority":3,"complete": False, "owner_id":1}]


def test_todoid (add_todo):
    response = client.get ('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() =={"id":1,"title":"Test","description":"Test","priority":3,"complete": False, "owner_id":1}

def test_create (add_todo):
    json_data = {"title":"Abenezer","description":"Gizaw","priority":3,"complete": True}
    response = client.post('/todo/add_todo', json=json_data)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestSessionLocal()
    item = db.query(Todos). filter (Todos.id==2).first ()
    assert item.complete ==json_data.get('complete')
    assert item.description == json_data.get ('description')

def test_update (add_todo):
    json_data = {"title":"Abenezer","description":"Gizaw","priority":3,"complete": True}
    response = client.put('/todo/update_todo/1',json= json_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    item = db.query (Todos).filter(Todos.id ==1).first()
    assert item.priority ==json_data.get ('priority')
    assert item.description == json_data.get ('description')

def test_update_not_found (add_todo):
    json_data = {"title":"Abenezer","description":"Gizaw","priority":3,"complete": True}
    response = client.put('/todo/update_todo/45',json= json_data)
    assert response.status_code == 404
    assert response.json()== {'detail': 'Item not found'}


    
def test_delete (add_todo):
    response = client.delete('/todo/delete_todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    items = db.query(Todos).all()
    assert len(items)==0
    