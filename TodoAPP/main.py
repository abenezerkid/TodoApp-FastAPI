#this page binds the model and detabase.py files and acomplish to create the database

from .routers import auth, todos, admin, users
from fastapi import FastAPI, status, Request
from .models import Base
from .database import engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory='TodoAPP/templates')
app.mount("/static",StaticFiles(directory='TodoAPP/static'), name="static")


Base.metadata.create_all(bind=engine) # table creation happen here, and if the table doesn't exist in models, it creates it when we run the program
# crete_all works to create the tables if it's not already created

#now we have to make it consumeable by the api app
#create the dependecy
@app.get("/")
async def test():
    return RedirectResponse(url="/todos/todo-page", status_code= status.HTTP_302_FOUND)

@app.get ('/test_pytest', status_code= status.HTTP_200_OK)
def test_pytest ():
    return {'test': 'successful'}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)