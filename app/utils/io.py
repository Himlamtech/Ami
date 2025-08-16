import json


def read_file(file_path: str) -> str:
    """Read a file and return its content."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(file_path: str, content: str) -> None:
    """Write content to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def load_json(file_path: str) -> dict:
    """Load content from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path: str, content: dict) -> None:
    """Save content to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
