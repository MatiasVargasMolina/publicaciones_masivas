import requests
from .config import MELI_TOKEN_URL, MELI_CLIENT_ID, MELI_CLIENT_SECRET, MELI_REDIRECT_URI


def exchange_code_for_token(code: str) -> dict:
    response = requests.post(
        MELI_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": MELI_CLIENT_ID,
            "client_secret": MELI_CLIENT_SECRET,
            "code": code,
            "redirect_uri": MELI_REDIRECT_URI,
        },
        timeout=15,
    )

    response.raise_for_status()
    return response.json()