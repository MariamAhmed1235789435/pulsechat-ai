from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from .database import create_tables
from .routers import leads, admin

# Create FastAPI app
app = FastAPI(title="PulseChat AI API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates for admin dashboard
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BACKEND_DIR, "templates"))

# Include routers
app.include_router(leads.router)
app.include_router(admin.router)

# Frontend directory (parent of backend)
FRONTEND_DIR = os.path.dirname(BACKEND_DIR)


# Serve frontend static files
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/sectors/{filename}", response_class=HTMLResponse)
async def serve_sector(filename: str):
    filepath = os.path.join(FRONTEND_DIR, "sectors", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return HTMLResponse("<h1>404</h1>", status_code=404)


# Serve static assets (CSS, JS, images)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# Catch-all for frontend static files (styles.css, script.js, image.png)
@app.get("/{filename:path}")
async def serve_static_file(filename: str):
    # Don't serve admin or api routes
    if filename.startswith("api/") or filename.startswith("admin"):
        return HTMLResponse("<h1>404</h1>", status_code=404)

    filepath = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(filepath):
        return FileResponse(filepath)
    return HTMLResponse("<h1>404</h1>", status_code=404)


# Create database tables on startup
@app.on_event("startup")
def startup():
    create_tables()
    print("PulseChat AI Backend is running!")
    print("Landing page: http://localhost:8000")
    print("Admin dashboard: http://localhost:8000/admin")
    print("API docs: http://localhost:8000/docs")
