import json
from pathlib import Path

TOKEN_FILE = Path("meli_token.json")


def guardar_token(token_data: dict):
    with open(TOKEN_FILE, "w", encoding="utf-8") as file:
        json.dump(token_data, file, indent=4)


def cargar_token() -> dict | None:
    if not TOKEN_FILE.exists():
        return None

    with open(TOKEN_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def obtener_access_token() -> str | None:
    token_data = cargar_token()

    if not token_data:
        return None

    return token_data.get("access_token")