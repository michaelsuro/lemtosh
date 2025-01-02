from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.database import engine, Base
from app.api import auth
from app.services.auth import get_current_user

app = FastAPI(title="Lemtosh")

# Create database tables
print("Creating database tables...") 
Base.metadata.create_all(bind=engine)
print("Database tables created successfully")  

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root(request: Request, user=Depends(get_current_user)):
    # If we get here, the user is authenticated
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "username": user.username}
    )

@app.exception_handler(401)
async def unauthorized_handler(request, exc):
    return RedirectResponse(url="/auth/login")