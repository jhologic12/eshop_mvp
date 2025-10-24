# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.database import init_db
from pathlib import Path
import os
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

app = FastAPI(title="E-Shop MVP Backend")

# 🔹 Crear tablas al iniciar la app
init_db()

# 🔹 Montar carpeta de archivos estáticos
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    raise RuntimeError(f"Directory '{STATIC_DIR}' does not exist")

# 🔹 Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Incluir todos los routers
app.include_router(api_router)
