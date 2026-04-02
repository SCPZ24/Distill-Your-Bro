from pathlib import Path
import re
from typing import List, Tuple
from backend.models.model import ModelManager


class Session:
    def __init__(self, bro_name: str, config_path: str = "config.yaml"):
        self.bro_name = bro_name
        self._safe_bro_name = self._to_safe_name(bro_name)
        self._model = ModelManager.get_instance(config_path).get_model()
        self._system_prompt = self._load_soul_prompt(self._safe_bro_name)
        self._history: List[Tuple[str, str]] = []

    def ask(self, user_message: str) -> str:
        if not isinstance(user_message, str) or not user_message.strip():
            raise ValueError("user_message 不能为空")

        prompt = self._build_prompt(user_message)
        reply = self._model.generate(prompt)
        self._history.append(("user", user_message))
        self._history.append(("bro", reply))
        return reply

    def messages(self) -> List[Tuple[str, str]]:
        return list(self._history)

    def reset(self) -> None:
        self._history.clear()

    def _build_prompt(self, user_message: str) -> str:
        lines: List[str] = []
        lines.append(self._system_prompt)
        lines.append(f"兄弟的名字是{self.bro_name}")
        for role, content in self._history:
            if role == "user":
                lines.append(f"用户：{content}")
            else:
                lines.append(f"{self.bro_name}：{content}")
        lines.append(f"用户：{user_message}")
        lines.append(f"{self.bro_name}：")
        return "\n".join(lines)

    def _load_soul_prompt(self, safe_bro_name: str) -> str:
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / "souls" / f"{safe_bro_name}_SOUL.md"
        if not path.exists():
            raise FileNotFoundError(f"未找到灵魂文件: {path}")
        return path.read_text(encoding="utf-8")

    def _to_safe_name(self, bro_name: str) -> str:
        safe = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "_", bro_name).strip("._-")
        return safe or "BRO"
