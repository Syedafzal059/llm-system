from app.services.models import cheap_model, expensive_model


class ModelRouter:
    """
    Routers request to appropriate model based on rules
    """

    def __init__(self) -> None:
        self.threshold_length = 50 

    async def route(self, prompt:str) -> str:
        if len(prompt)<self.threshold_length:
            return await cheap_model(prompt)

        else: 
            return await expensive_model(prompt)

    