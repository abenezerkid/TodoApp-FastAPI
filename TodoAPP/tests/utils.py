from sqlalchemy import create_engine, text, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # this is new importing the sqlalchemy pool
from fastapi.testclient import TestClient
from ..database import Base
import pytest
from ..models import Todos, Users
from ..main import app
from passlib.context import CryptContext

Test_SQLALCHEMY_DATABASE_URL='sqlite:///./testbd.bd' 
engine = create_engine(Test_SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False},
                        poolclass= StaticPool) # new change about poolclass
TestSessionLocal = sessionmaker(autocommit =False, autoflush= False, bind =engine)

Base.metadata.create_all(bind=engine) # crate all the tables from base, and model is a child of base class from database

pwd_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
def override_get_db ():
    db = TestSessionLocal()
    try: 
        yield db #this is actually interesting makes the database running till the route completed,
        #once it's done pass it to db.cloe  close the session 
    finally:
        db.close()

def override_ger_currenet_user():
    return {'username':'test', 'id':1 , 'user_role':'admin'}

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

@pytest.fixture
def add_user ():
    create_user_model = Users (
                     email = 'user.email',
                     username = 'user.username',
                     first_name = 'user.first_name',
                     last_name = 'user.last_name',
                     hashed_password = pwd_context.hash('password'),
                     role = 'admin',
                     is_active = True,
                     phone_number = 'user.phone_number'
                     )
        
    db = TestSessionLocal()
    db.add(create_user_model)
    db.commit()

    yield db
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users;'))
        connection.commit()
        connection.close()