from fastapi import FastAPI
from app.routes.assignment_routes import routes

app = FastAPI()

app.include_router(routes, prefix="/api")