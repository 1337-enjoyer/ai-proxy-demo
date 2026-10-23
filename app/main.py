from fastapi import FastAPI
from app.core.users import fastapi_users, auth_backend
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.api.routes import chat  # твой chat-роут оставляем

app = FastAPI(title="AI Provider Demo")

# Готовые роуты от fastapi-users
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Твой chat-роут (там теперь используешь current_active_user)
app.include_router(chat.router)

@app.get("/health")
async def health():
    return {"status": "ok"}