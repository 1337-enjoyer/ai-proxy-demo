# /chat, /chat/stream (твой провайдер)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import AsyncOpenAI

from app.api.deps import get_current_user
from app.models.user import User

from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY,
                     base_url=settings.OPENAI_BASE_URL)


class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4.1:mock-text"


@router.post("/stream")
async def chat_stream(req: ChatRequest, user: User = Depends(get_current_user)):
    async def gen():
        stream = await client.chat.completions.create(
            model=req.model,
            messages=[{"role": "user", "content": req.message}], stream=True
        )
        async for chunk in stream:
            if delta := chunk.choices[0].delta.content:
                yield f"data: {delta}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
