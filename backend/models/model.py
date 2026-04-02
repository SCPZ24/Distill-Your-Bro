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
        if isinstance(config, str):
            return self.init_from_yaml(config)
        if not isinstance(config, dict):
            raise ValueError("config 必须是 dict 或 config.yaml 路径字符串")

        provider = str(config.get("provider", "")).strip().lower()
        model_cls = self._model_class_from_provider(provider, config.get("provider"))
        self.model = model_cls(dict(config))
        return self.model

    def init_from_yaml(self, path: str = "config.yaml") -> Model:
        raw = self._load_yaml(path)
        model_cfg = raw.get("model", raw)
        if not isinstance(model_cfg, dict):
            raise ValueError("config.yaml 中 model 配置格式错误")

        provider_raw = model_cfg.get("provider")
        provider = str(provider_raw or "").strip().lower()
        if not provider:
            raise ValueError("config.yaml 缺少 provider")

        model_cls = self._model_class_from_provider(provider, provider_raw)
        cfg: Dict[str, Any] = {}
        for key in ("provider", "name", "api_key", "model_name", "base_url"):
            if key in model_cfg:
                cfg[key] = model_cfg[key]
        self.model = model_cls(cfg)
        return self.model

    def _model_class_from_provider(
        self, provider: str, provider_raw: object
    ) -> Type[Model]:
        if provider in {"deepseek", "deep_seek"}:
            from backend.models.model_from_provider.DeepSeekProvider import DeepSeekModel

            return DeepSeekModel
        if provider in {"volcengine", "volces", "ark", "doubao"}:
            from backend.models.model_from_provider.VolcengineProvider import VolcengineModel

            return VolcengineModel
        raise ValueError(f"不支持的 provider: {provider_raw}")

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
