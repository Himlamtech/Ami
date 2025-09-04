import json
from typing import Any


def read_file(file_path: str) -> str:
    """Read a file and return its content."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write content to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def load_json(file_path: str) -> dict[Any, Any]:
    """Load content from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        result = json.load(f)
        # Ensure we return a dict type
        if not isinstance(result, dict):
            raise ValueError(
                f"Expected dict from JSON file {file_path}, got {type(result)}"
            )
        return result


def save_json(file_path: str, content: dict[Any, Any]) -> None:
    """Save content to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
