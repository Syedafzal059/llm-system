from fastapi import FastAPI
from app.routes import router as generate_router

app = FastAPI(title="Mini LLM Backend")

app.include_router(generate_router, prefix="/generate", tags=["generate"])

@app.get("/health")
async def health():
    return {"status": "I am healthy :)"}

    


