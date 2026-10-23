# Точка входа FastAPI
from fastapi import FastAPI

from app.api.routes import auth, chat

app = FastAPI(title="AI Provider Demo")

app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
