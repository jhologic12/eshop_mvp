# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db

app = FastAPI(title="E-Shop MVP Backend")

# 🔹 Crear tablas al iniciar la app
init_db()

# 🔹 Montar carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🔹 Configuración CORS (para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # o lista de URLs de tu frontend: ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Incluir todos los routers
app.include_router(api_router)
