from fastapi import FastAPI
from .routers import bids, projects, users, admins,ratings,dashboard,notification
from app import auth


app = FastAPI()

app.include_router(dashboard.router)
app.include_router(bids.router)
app.include_router(projects.router)
app.include_router(users.router)
app.include_router(admins.router)
app.include_router(auth.router)
app.include_router(ratings.router)
app.include_router(notification.router)

@app.get("/")
async def root():
    return {"status": "ok"}