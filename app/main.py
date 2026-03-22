from fastapi import FastAPI
from app.routes import generate, batch

app = FastAPI(title="Mini LLM Backend")

app.include_router(generate.router, prefix="/generate", tags=["generate"])
app.include_router(batch.router, prefix="/generate/batch", tags=["batch"])


@app.get("/health")
async def health():
    return {"status": "I am healthy :)"}

    


