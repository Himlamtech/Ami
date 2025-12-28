import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parents[1]
POSTMAN_DIR = ROOT / "tests" / "postman"
LOG_DIR = POSTMAN_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _flatten_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for item in items:
        if "item" in item and isinstance(item["item"], list):
            result.extend(_flatten_items(item["item"]))
        else:
            result.append(item)
    return result


def _resolve_vars(text: str, variables: Dict[str, str]) -> str:
    if not text:
        return text
    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def _load_collection(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_variables(collection: Dict[str, Any]) -> Dict[str, str]:
    variables = {}
    for var in collection.get("variable", []):
        if isinstance(var, dict) and var.get("key"):
            variables[var["key"]] = str(var.get("value", ""))
    return variables


def _request_from_item(
    item: Dict[str, Any], variables: Dict[str, str]
) -> Optional[Dict[str, Any]]:
    request = item.get("request")
    if not isinstance(request, dict):
        return None

    method = request.get("method", "GET").upper()
    url = request.get("url", {})
    raw_url = url.get("raw") or ""
    raw_url = _resolve_vars(raw_url, variables)

    headers = {}
    for header in request.get("header", []) or []:
        if not isinstance(header, dict):
            continue
        key = header.get("key")
        value = _resolve_vars(header.get("value", ""), variables)
        if key:
            headers[key] = value

    body = None
    body_info = request.get("body", {})
    if isinstance(body_info, dict) and body_info.get("mode") == "raw":
        raw_body = body_info.get("raw") or ""
        body = _resolve_vars(raw_body, variables).encode("utf-8")

    return {
        "name": item.get("name", "Unnamed Request"),
        "method": method,
        "url": raw_url,
        "headers": headers,
        "body": body,
    }


def _run_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    start = time.time()
    req = urllib.request.Request(
        request_data["url"],
        data=request_data["body"],
        headers=request_data["headers"],
        method=request_data["method"],
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
            status = response.status
    except Exception as exc:
        body = str(exc)
        status = 0
    latency_ms = int((time.time() - start) * 1000)
    return {
        "name": request_data["name"],
        "method": request_data["method"],
        "url": request_data["url"],
        "status": status,
        "latency_ms": latency_ms,
        "body": body,
    }


def run_collection(path: Path) -> Dict[str, Any]:
    collection = _load_collection(path)
    variables = _build_variables(collection)
    items = _flatten_items(collection.get("item", []))
    requests = []
    for item in items:
        request_data = _request_from_item(item, variables)
        if request_data:
            requests.append(request_data)

    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(_run_request, req) for req in requests]
        for future in as_completed(futures):
            results.append(future.result())

    summary = {
        "collection": collection.get("info", {}).get("name", path.name),
        "count": len(results),
        "success": sum(1 for r in results if r["status"] and r["status"] < 400),
        "failed": sum(1 for r in results if not r["status"] or r["status"] >= 400),
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }

    log_path = LOG_DIR / f"{path.stem}_{int(time.time())}.json"
    log_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    collections = [
        path for path in POSTMAN_DIR.rglob("*.json") if "logs" not in path.parts
    ]
    if not collections:
        print("No collections found under", POSTMAN_DIR)
        return

    print("Running", len(collections), "collections...")
    for path in collections:
        summary = run_collection(path)
        print(
            f"{summary['collection']}: {summary['success']}/{summary['count']} passed"
        )


if __name__ == "__main__":
    main()
