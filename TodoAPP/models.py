#this page is to configure the model of the table or database like column, PK and others
from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

class Users (Base):
    __tablename__ ='users'
    id = Column(Integer, primary_key= True, index= True) # sqlalchemy Innteger primary key is alway on auto incremment. 
    # but except in sqllite both mysql and postgresql need to say autoincrement true
    email = Column(String, unique=True)
    username = Column (String,unique = True)
    first_name = Column(String)
    last_name = Column (String)
    hashed_password = Column(String)
    is_active = Column (Boolean, default = True)
    role = Column (String)
    phone_number = Column(String)


class Todos(Base):
    __tablename__ ='todos'
    id = Column(Integer, primary_key= True, index= True)
    title =Column(String)
    description =Column(String)
    priority = Column(Integer)
    complete = Column (Boolean, default= False) # Complete is updated to 'complete'
    owner_id = Column (Integer, ForeignKey(Users.id))
