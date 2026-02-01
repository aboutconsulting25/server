from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(prompt_name: str) -> str:
    path = PROMPT_DIR / f"{prompt_name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")
