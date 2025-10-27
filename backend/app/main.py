# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.database import init_db
from pathlib import Path
import os

# URL del frontend (local o producción)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

origins = [
    "https://tienda-virtual-e-shop.onrender.com",  # tu frontend
    "http://localhost:5173"  # para desarrollo local
]

app = FastAPI(title="E-Shop MVP Backend")

# 🔹 Crear tablas al iniciar la app
init_db()

# 🔹 Carpeta estática segura
BASE_DIR = Path(__file__).resolve().parent.parent  # apunta a backend/
STATIC_DIR = BASE_DIR / "static"

# Debug: imprime path para verificar en Render
print(f"[DEBUG] STATIC_DIR = {STATIC_DIR}, exists: {STATIC_DIR.exists()}")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
else:
    raise RuntimeError(f"Directory '{STATIC_DIR}' does not exist")

# 🔹 Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # Permite estos orígenes
    allow_credentials=True,
    allow_methods=["*"],     # Permite GET, POST, PUT, DELETE...
    allow_headers=["*"],     # Permite todos los headers
)

# 🔹 Incluir todos los routers
app.include_router(api_router)
