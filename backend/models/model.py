from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

class Model(ABC):
    @abstractmethod
    def __init__(self, config: dict):
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class ModelManager:
    _instance: Optional["ModelManager"] = None

    @classmethod
    def get_singleton_instance(cls) -> "ModelManager":
        return cls()

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

    def init_from_config(self, path: str = "config.yaml") -> Model:
        raw = self._load_yaml(path)
        model_cfg = raw.get("model", raw)
        if not isinstance(model_cfg, dict):
            raise ValueError("config.yaml 中 model 配置格式错误")

        provider_raw = model_cfg.get("provider")
        if not provider_raw:
            raise ValueError("config.yaml 缺少 provider")

        model_cls = self._model_class_from_provider(str(provider_raw))
        cfg: Dict[str, Any] = dict(model_cfg)
        self.model = model_cls(cfg)
        return self.model

    def _model_class_from_provider(self, provider: str) -> Type[Model]:
        match provider:
            case "DeepSeek":
                from backend.models.model_from_provider.DeepSeekProvider import DeepSeekModel

                return DeepSeekModel
            case "Volcengine":
                from backend.models.model_from_provider.VolcengineProvider import VolcengineModel

                return VolcengineModel
            case _:
                raise ValueError(f"不支持的 provider: {provider}")

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        text = open(path, "r", encoding="utf-8").read()
        try:
            import yaml  # type: ignore

            data = yaml.safe_load(text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

        data = self._parse_simple_yaml(text)
        if not isinstance(data, dict) or not data:
            raise ValueError("config.yaml 解析失败")
        return data

    def _parse_simple_yaml(self, text: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        current_map: Optional[Dict[str, Any]] = None
        current_key: Optional[str] = None

        for raw in text.splitlines():
            line = raw.rstrip()
            if not line.strip():
                continue
            if line.lstrip().startswith("#"):
                continue

            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()
            if ":" not in stripped:
                continue

            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()

            if not value:
                current_key = key
                if key not in out or not isinstance(out.get(key), dict):
                    out[key] = {}
                current_map = out[key]
                continue

            if value.startswith("#"):
                value = ""

            v = value.strip().strip("\"'").strip("`").strip()

            if indent == 0:
                out[key] = v
                current_map = None
                current_key = None
            else:
                if current_map is None:
                    if current_key is None:
                        continue
                    maybe = out.get(current_key)
                    if isinstance(maybe, dict):
                        current_map = maybe
                    else:
                        out[current_key] = {}
                        current_map = out[current_key]
                current_map[key] = v

        return out
