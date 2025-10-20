# app/main.py
from fastapi import FastAPI
from app.api.routes import router as api_router


from app.core.database import init_db



app = FastAPI(title="E-Shop MVP Backend")

# 🔹 Crear tablas al iniciar la app
init_db()
# Incluir todos los routers
app.include_router(api_router)

