"""Пример реальных HTTP-запросов, использует только стандартную библиотеку Python."""
import json
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = "http://127.0.0.1:8000"

def request(method, path, data=None):
    payload = json.dumps(data, ensure_ascii=False).encode() if data is not None else None
    req = Request(BASE + path, data=payload, method=method, headers={"Content-Type":"application/json"})
    try:
        with urlopen(req, timeout=10) as response:
            body = response.read().decode()
            print(method, path, '->', response.status, body)
            return json.loads(body) if body else None
    except HTTPError as error:
        print(method, path, '->', error.code, error.read().decode())
        raise

if __name__ == "__main__":
    categories = request("GET", "/api/categories")
    item = request("POST", "/api/parts", {"name":"Салонный фильтр", "description":"Демонстрация полного цикла работы REST API.", "article":"DEMO-" + uuid.uuid4().hex[:8].upper(), "category_id":categories[0]["id"], "price":"790.50"})
    path = f"/api/parts/{item['id']}"
    try:
        request("GET", "/api/parts")
        request("GET", path)
        request("PATCH", path, {"price":"849.90"})
    finally:
        request("DELETE", path)
