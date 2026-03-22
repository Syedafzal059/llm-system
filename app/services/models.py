import asyncio

async def cheap_model(prompt:str) -> str:
    await asyncio.sleep(0.2) # simulating fast response
    return f"[Cheap Model]{prompt}"

async def expensive_model(prompt: str) -> str:
    await asyncio.sleep(1.5) # simulating slow response
    return f"[Expensive Model] {prompt}"


#streaming version

async def expensive_model_stream(prompt: str):
    #simulate token by token streaming 
    tokens = prompt.split()
    for token in tokens:
        await asyncio.sleep(0.1)
        yield token 
