from pathlib import Path
import re
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

WORK_DIRECTORY = REPO_ROOT / "souls"

def _to_safe_name(bro_name: str) -> str:
    safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "_", bro_name).strip("._-")
    return safe_name or "BRO"


def _split_front_matter(markdown: str) -> tuple[Optional[str], str]:
    if not markdown.startswith("---"):
        return None, markdown

    normalized = markdown.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, markdown

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            front = "\n".join(lines[1:i])
            body = "\n".join(lines[i + 1 :])
            return front, body.lstrip("\n")
    return None, markdown


def _extract_created_at(front_matter: str) -> Optional[str]:
    for line in front_matter.splitlines():
        if not line.strip():
            continue
        if not line.lstrip().startswith("created_at:"):
            continue
        raw = line.split(":", 1)[1].strip()
        if raw.startswith(("'", '"')) and raw.endswith(("'", '"')) and len(raw) >= 2:
            return raw[1:-1]
        return raw
    return None


def soul_path(bro_name: str) -> Path:
    safe_name = _to_safe_name(bro_name)
    return WORK_DIRECTORY / f"{safe_name}.md"


def store_soul(bro_name: str, soul_markdown: str, created_at: str) -> str:
    safe_name = _to_safe_name(bro_name)

    WORK_DIRECTORY.mkdir(parents=True, exist_ok=True)
    out_path = WORK_DIRECTORY / f"{safe_name}.md"

    _, body = _split_front_matter(soul_markdown)
    created_at_yaml = created_at.replace('"', '\\"')
    content = f'---\ncreated_at: "{created_at_yaml}"\n---\n\n{body.lstrip() if body else ""}'
    out_path.write_text(content, encoding="utf-8")
    return safe_name


def read_soul(bro_name: str) -> Optional[str]:
    in_path = soul_path(bro_name)
    if not in_path.exists():
        return None

    front, body = _split_front_matter(in_path.read_text(encoding="utf-8"))
    return body


def export_soul_markdown(bro_name: str) -> Optional[tuple[str, str]]:
    path = soul_path(bro_name)
    if not path.exists():
        return None
    return path.name, path.read_text(encoding="utf-8")


def view_soul() -> list[tuple[str, str]]:
    if not WORK_DIRECTORY.exists():
        return []

    souls: list[tuple[str, str]] = []
    for entry in WORK_DIRECTORY.iterdir():
        if entry.is_file() and entry.suffix == ".md":
            front, _ = _split_front_matter(entry.read_text(encoding="utf-8"))
            created_at = _extract_created_at(front) if front is not None else None
            souls.append((entry.stem, created_at or ""))
    souls.sort(key=lambda x: x[0])
    return souls


def remove_soul(bro_name: str) -> bool:
    path = soul_path(bro_name)
    if not path.exists():
        return False
    path.unlink()
    return True
