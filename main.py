import json
from fastapi import FastAPI
from mongoengine import connect
from pymongo import settings

from models import Employee, User

app = FastAPI()
connect(db='hrms', host='localhost', port=27017)


# @app.get('/')
# def hello_world():
#     return {"message": "Hello World"}


@app.get('/all_employee')
def all_employee():
    employees = json.loads(Employee.objects().to_json())
    return {"employees": employees}


# sign up
from pydantic import BaseModel


class NewUser(BaseModel):
    username: str
    password: str


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


@app.post('/sign_up')
def sign_up(new_user: NewUser):
    user = User(username=new_user.username
                , password=get_password_hash(new_user.password))

    user.save()
    return {"message": "Sign up successful"}


# for token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def authenticate_user(username, password):
    try:
        user = json.loads(User.objects.get(username=username).to_json())
        password_check = pwd_context.verify(password, user['password'])
        return password_check
    except User.DoesNotExist:
        return False


from datetime import timedelta, datetime
from jose import jwt

SECRET_KEY = 'ca536adaa0f469a32a0ade33bbe1658ccf148effd89ea6c32cb551eb608a6fb1d08ec8c7eb6722ac1a4104566f4e1dcbab9e17ba7d3ce388c95190e0e3c05f91'


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm='HS256')
    return encoded_jwt


@app.post('/token')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    print(username, password)
    if authenticate_user(username, password):
        access_token = create_access_token(
            data={"sub": username}, expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


@app.get('/')
def hello_world(token: str = Depends(oauth2_scheme)):
    return {"token": token}
