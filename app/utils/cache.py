from typing import Dict 

class InMemoryCache:
    """
    Simple in-memory cache using Python Dict
    """

    def __init__(self):
        self.store: Dict[str, str] = {}

    def get(self, key:str):
        return self.store.get(key)
    
    def set(self, key:str, value: str):
        self.store[key] = value