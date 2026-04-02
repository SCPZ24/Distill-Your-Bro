from abc import ABC, abstractmethod
from typing import Optional, Type

class Model(ABC):
    @abstractmethod
    def __init__(self, config: dict):
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class ModelManager:
    _instance: Optional["ModelManager"] = None

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None
        return cls._instance

    def set_model(self, model: Model) -> None:
        self.model = model

    def get_model(self) -> Model:
        if self.model is None:
            raise ValueError("model 未初始化")
        return self.model

    def init_from_config(self, config: object) -> Model:
        if not isinstance(config, dict):
            raise ValueError("config 必须是 dict")

        provider = str(config.get("provider", "")).strip().lower()
        model_cls: Optional[Type[Model]] = None

        if provider in {"deepseek", "deep_seek"}:
            from backend.models.model_from_provider.DeepSeekProvider import DeepSeekModel

            model_cls = DeepSeekModel

        if model_cls is None:
            raise ValueError(f"不支持的 provider: {config.get('provider')}")

        self.model = model_cls(config)
        return self.model
