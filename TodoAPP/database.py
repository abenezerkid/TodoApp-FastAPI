#This page is actually configuring the databae connection, creating location
# #the engine and the session
# most of the time same from projects to projects
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
#SQLALCHEMY_DATABASE_URL='sqlite:///./todosapp.db' #create the location of the db in fastAPI application
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")
#SQLALCHEMY_DATABASE_URL='postgresql://postgres:test1234!@localhost/TodoApplicationDatabase' #postgresql database the test1234! is the password for the database
#engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
engine = create_engine(DATABASE_URL) # postgresql creating engine
SessionLocal = sessionmaker(autocommit =False, autoflush= False, bind =engine)

Base = declarative_base() # will be a parent class for the model class we creating


