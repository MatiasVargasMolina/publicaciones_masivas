import requests


class ShippingClient:
    BASE_URL = "https://api.mercadolibre.com"

    def __init__(self, access_token: str):
        self.access_token = access_token

    def get_user_id(self):
        response = requests.get(
            f"{self.BASE_URL}/users/me",
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            timeout=10,
        )

        response.raise_for_status()
        return response.json()["id"]

    def get_free_shipping_options(
        self,
        user_id: int,
        publication_id: str,
    ):
        url = f"{self.BASE_URL}/users/{user_id}/shipping_options/free"

        params = {
            "item_id": publication_id
        }

        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}"
            },
            params=params,
            timeout=20,
        )

        print("URL:", response.url)
        print("STATUS:", response.status_code)
        print("BODY:", response.text)

        if response.status_code >= 400:
            raise Exception(
                f"Error consultando Mercado Envíos free: "
                f"{response.status_code} - {response.text}"
            )

        return response.json()