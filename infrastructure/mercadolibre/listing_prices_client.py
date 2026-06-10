import requests


class ListingPricesClient:
    BASE_URL = "https://api.mercadolibre.com"

    def __init__(self, access_token: str):
        self.access_token = access_token

    def get_listing_prices(
        self,
        site_id: str,
        price: float,
        category_id: str | None = None,
        listing_type_id: str | None = None,
        currency_id: str | None = None,
        logistic_type: str | None = None,
        quantity: int | None = None,
    ):
        url = f"{self.BASE_URL}/sites/{site_id}/listing_prices"

        params = {
            "price": price
        }

        if category_id:
            params["category_id"] = category_id

        if listing_type_id:
            params["listing_type_id"] = listing_type_id

        if currency_id:
            params["currency_id"] = currency_id

        if logistic_type:
            params["logistic_type"] = logistic_type

        if quantity:
            params["quantity"] = quantity

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code >= 400:
            raise Exception(
                f"Error consultando listing_prices: "
                f"{response.status_code} - {response.text}"
            )

        return response.json()