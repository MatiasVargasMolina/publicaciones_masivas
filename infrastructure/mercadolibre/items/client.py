import requests


BASE_URL = "https://api.mercadolibre.com"


def get_user_items(user_id: int, access_token: str, limit: int = 50, offset: int = 0) -> dict:
    url = f"{BASE_URL}/users/{user_id}/items/search"

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "limit": limit,
            "offset": offset,
            "status": "active",
        },
        timeout=20,
    )

    response.raise_for_status()
    return response.json()


def get_items_detail(item_ids: list[str], access_token: str) -> list[dict]:
    if not item_ids:
        return []

    ids = ",".join(item_ids)

    response = requests.get(
        f"{BASE_URL}/items",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "ids": ids,
        },
        timeout=20,
    )

    response.raise_for_status()

    return [item["body"] for item in response.json() if item.get("code") == 200]