from fastapi import FastAPI

from routes import auth, users
from schemas import Message

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', response_model=Message)
def read_root():
    return Message(message='Hello, World!')
