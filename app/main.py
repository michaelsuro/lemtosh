from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.database import engine, Base
from app.api import auth, chat, models
from app.services.auth import get_current_user
from app.services.llm import llm_service  # Import the service

app = FastAPI(title="LLM Playground")

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize LLM service
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("Starting up server...")
    llm_service.initialize()
    print("Server startup complete")

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(models.router, prefix="/api", tags=["models"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}