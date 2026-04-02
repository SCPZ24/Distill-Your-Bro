from backend.models.model import ModelManager
from pathlib import Path
import re

model_manager = ModelManager.get_instance()

model = model_manager.get_model()

def extract_soul(bro_name: str, meta_prompt: str, chat_log: str):
    prompt = f"{meta_prompt}\n兄弟的名字是{bro_name}\n{chat_log}"
    response = model.generate(prompt)
    safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "_", bro_name).strip("._-")
    if not safe_name:
        safe_name = "BRO"

    repo_root = Path(__file__).resolve().parents[2]
    souls_dir = repo_root / "souls"
    souls_dir.mkdir(parents=True, exist_ok=True)

    out_path = souls_dir / f"{safe_name}_SOUL.md"
    out_path.write_text(response, encoding="utf-8")
    return response
