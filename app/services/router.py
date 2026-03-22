import asyncio
from app.services.models import cheap_model, expensive_model
from app.utils.cache import InMemoryCache
from app.services.fallback import fallback_model
from app.utils.file_usage_tracker import log_usage

class ModelRouter:
    """
    Routers request to appropriate model based on rules
    """

    def __init__(self) -> None:
        self.threshold_length = 50 
        self.cache = InMemoryCache()
        self.retry_count = 2


    async def route(self, prompt:str, user_id:str = "anonymous") -> str:
        #check cache first
        cached_response = self.cache.get(prompt)
        if cached_response:
            log_usage(prompt, "cached", cached_response, user_id)
            return f"[Cached]{cached_response}"

        # Determine prmary model 
        primary = cheap_model if len(prompt) <self.threshold_length else expensive_model

        #Try primary model with retry 
        for attempt in range(self.retry_count):
            try:
                response = await primary(prompt)
                self.cache.set(prompt, response)
                log_usage(prompt, primary.__name__, response, user_id)
                return response
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}")
                await asyncio.sleep(0.5)

        # if all retries fail, use fallback
        fallback_response = await fallback_model(prompt)
        #store in cache
        self.cache.set(prompt, fallback_response)
        log_usage(prompt, "fallback_model", fallback_response, user_id)
        return f"[Fallback] {fallback_response}"