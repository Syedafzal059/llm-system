from fastapi import APIRouter
from pydantic import BaseModel
from app.services.router import ModelRouter

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

