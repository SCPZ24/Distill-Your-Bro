from pathlib import Path
import re
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

WORK_DIRECTORY = REPO_ROOT / "chatlogstr"

def store_chat_log(bro_name: str, chat_log: str):
    safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "_", bro_name).strip("._-")
    if not safe_name:
        safe_name = "BRO"

    WORK_DIRECTORY.mkdir(parents=True, exist_ok=True)
    out_path = WORK_DIRECTORY / f"{safe_name}.txt"
    out_path.write_text(chat_log, encoding="utf-8")

def read_chat_log(bro_name: str) -> Optional[str]:
    safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "_", bro_name).strip("._-")
    if not safe_name:
        safe_name = "BRO"

    in_path = WORK_DIRECTORY / f"{safe_name}.txt"
    if not in_path.exists():
        return None

    return in_path.read_text(encoding="utf-8")
