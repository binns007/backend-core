from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
import database

from routes import auth, dealership, branch, employee, form, websocket
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()



origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=database.engine)

app.include_router(auth.router)
app.include_router(dealership.router)
app.include_router(branch.router)
app.include_router(employee.router)
app.include_router(form.router)
app.include_router(websocket.router)



