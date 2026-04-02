from backend.models.model import Model
from typing import Optional
from openai import OpenAI

class VolcengineModel(Model):
    def __init__(self, config: dict):
        try:
            self.name = config["name"]
            self.api_key = config["api_key"]
            self.model_name = config["model_name"]
            self.base_url = config["base_url"]
        except KeyError as e:
            raise ValueError(f"Volcengine 配置缺少字段: {e.args[0]}") from e
