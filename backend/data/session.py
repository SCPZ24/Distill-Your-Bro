from pathlib import Path
import json
import re
from typing import Optional, Union

from backend.data.soul import read_soul

REPO_ROOT = Path(__file__).resolve().parents[2]

WORK_DIRECTORY = REPO_ROOT / "sessions"

def _to_safe_id(session_id: str) -> str:
    safe = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "_", session_id).strip("._-")
    return safe or "SESSION"


def session_path(session_id: str) -> Path:
    return WORK_DIRECTORY / f"{_to_safe_id(session_id)}.json"

def _split_bro_messages(content: str) -> list[str]:
    return [m.strip() for m in re.split(r"[\s？。！.?!]+", str(content)) if m and m.strip()]


class Session:
    def __init__(self, session_id: str):
        self.session_id = _to_safe_id(session_id)
        path = session_path(self.session_id)
        if not path.exists():
            raise FileNotFoundError(f"Session not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.bro_name = data.get("bro_name", "")
        self.created_time = data.get("created_time", "")
        self.message_list = data.get("message_list", [])
        soul = read_soul(self.bro_name)
        self.soul_markdown = soul or ""

    def store(self):
        WORK_DIRECTORY.mkdir(parents=True, exist_ok=True)
        path = session_path(self.session_id)
        data = {
            "session_id": self.session_id,
            "bro_name": self.bro_name,
            "created_time": self.created_time,
            "message_list": self.message_list,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    def add_message(self, user_message: str, bro_message: Union[str, list[str]]):
        if isinstance(bro_message, list):
            bro_message = "\n".join([m for m in bro_message if m is not None])
        self.message_list.append([user_message, bro_message])

    def concatenate_prompt(self, user_message: str) -> str:
        lines: list[str] = []
        lines.append(f"你要扮演用户的好兄弟{self.bro_name}与用户对话。以下是对于兄弟的描述：")
        lines.append(self.soul_markdown)
        lines.append("现有对话：")
        history = self._concatenate_messages()
        if history:
            lines.append(history)
        lines.append(f"用户：{user_message}")
        lines.append(f"{self.bro_name}：")
        return "\n".join(lines)

    def _concatenate_messages(self) -> str:
        lines: list[str] = []
        for user_message, bro_message in self.message_list:
            lines.append(f"用户：{user_message}")
            bro_messages = _split_bro_messages(str(bro_message))
            if not bro_messages:
                lines.append(f"{self.bro_name}：")
                continue
            for m in bro_messages:
                lines.append(f"{self.bro_name}：{m}")
        return "\n".join(lines)


def new_session(session_id: str, bro_name: str, created_time: str):
    WORK_DIRECTORY.mkdir(parents=True, exist_ok=True)
    safe_id = _to_safe_id(session_id)
    path = session_path(safe_id)
    data = {
        "session_id": safe_id,
        "bro_name": bro_name,
        "created_time": created_time,
        "message_list": [],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

def view_session() -> list[tuple[str, str, str]]:
    if not WORK_DIRECTORY.exists():
        return []
    sessions: list[tuple[str, str, str]] = []
    for entry in WORK_DIRECTORY.iterdir():
        if entry.is_file() and entry.suffix == ".json":
            try:
                data = json.loads(entry.read_text(encoding="utf-8"))
                sessions.append(
                    (
                        data.get("session_id", entry.stem),
                        data.get("bro_name", ""),
                        data.get("created_time", ""),
                    )
                )
            except Exception:
                continue
    sessions.sort(key=lambda x: x[2] or "")
    return sessions


def remove_session(session_id: str) -> bool:
    path = session_path(session_id)
    if not path.exists():
        return False
    path.unlink()
    return True
