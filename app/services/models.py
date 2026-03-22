import asyncio

async def cheap_model(prompt:str) -> str:
    await asyncio.sleep(0.2)
    return f"[Cheap Model]{prompt}"

async def expensive_model(prompt: str) -> str:
    await asyncio.sleep(1.5)
    return f"[Expensive Model] {prompt}"

    