from fastapi import APIRouter
from pydantic import BaseModel 
from app.services.router import ModelRouter

router = APIRouter()
model_router = ModelRouter()

# Request Schema
class BatchRequest(BaseModel):
    prompts: list[str]
    user_id: str = "anonymous"


class BatchResponse(BaseModel):
    responses: list[str]


@router.post("/", response_model=BatchResponse)
async def generate_batch(request: BatchRequest):
    results = await model_router.batch_route(request.prompts, user_id=request.user_id)
    return {"responses": results}