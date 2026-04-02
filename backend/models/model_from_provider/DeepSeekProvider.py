from backend.models.model import Model

class DeepSeekModel(Model):
    def __init__(self, config: dict):
        self.name = config["name"]
        self.api_key = config["api_key"]
        self.model_name = config["model_name"]
        self.base_url = config["base_url"]
    
    def generate(self, prompt: str) -> str:
        pass