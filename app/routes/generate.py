from fastapi import APIRouter
from pydantic import BaseModel
from app.services.router import ModelRouter
from fastapi.responses import StreamingResponse
router = APIRouter()
model_router = ModelRouter()
class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    response: str

@router.post("/", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    # Route to appropriate model 
    output = await model_router.route(request.prompt)
    return {"response": output}

@router.post("/stream")
async def generate_stream(request: GenerateRequest):
    async def event_generator():
        async for token in model_router.stream_route(request.prompt):
            yield token
    return StreamingResponse(event_generator(), media_type="text/plain")
