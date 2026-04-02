from abc import ABC, abstractmethod
from model_from_provider import *

@ABC
class Model:
    @abstractmethod
    def __init__(self, config: dict):
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

