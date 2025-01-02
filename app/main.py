from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.database import engine, Base
from app.api import auth, chat, models
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
async def root(request: Request):
    try:
        # Note: We don't actually verify the token here since this is just the template
        # The frontend JavaScript will handle redirecting if there's no token
        return templates.TemplateResponse("home.html", {"request": request})
    except HTTPException:
        return RedirectResponse(url="/auth/login")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(models.router, prefix="/api", tags=["models"])

@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.exception_handler(401)
async def unauthorized_handler(request, exc):
    return RedirectResponse(url="/auth/login")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}