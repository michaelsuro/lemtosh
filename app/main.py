from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Lemtosh")

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}