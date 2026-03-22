from app.services.models import cheap_model

async def fallback_model(prompt: str) -> str:
    #simple fallback: always uses cheap_model

    return await cheap_model(prompt)


    