from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

WORK_DIRECTORY = REPO_ROOT / "prompts"

def load_prompt(prompt_markdown_name: str) -> str:
    prompt_path = WORK_DIRECTORY / prompt_markdown_name
    try:
        return prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Prompt markdown not found: {prompt_path}") from e
    except OSError as e:
        raise OSError(f"Failed to read prompt markdown: {prompt_path}") from e
