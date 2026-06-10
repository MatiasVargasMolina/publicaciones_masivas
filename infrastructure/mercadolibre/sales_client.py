import requests
from datetime import datetime, timedelta, timezone

from infrastructure.mercadolibre.oauth.token_storage import obtener_access_token


class MercadoLibreSalesClient:
    BASE_URL = "https://api.mercadolibre.com"

    def __init__(self):
        self.access_token = obtener_access_token()

        if not self.access_token:
            raise ValueError("No hay access_token de MercadoLibre guardado")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def get_me(self):
        response = requests.get(
            f"{self.BASE_URL}/users/me",
            headers=self._headers(),
            timeout=30,
        )

        if response.status_code >= 400:
            raise ValueError(
                f"Error obteniendo usuario ML: {response.status_code} - {response.text}"
            )

        return response.json()

    def get_orders_by_seller(
        self,
        seller_id: str,
        days: int = 30,
        limit: int = 50,
        offset: int = 0,
    ):
        date_from = datetime.now(timezone.utc) - timedelta(days=days)

        params = {
            "seller": seller_id,
            "order.date_created.from": date_from.isoformat(),
            "sort": "date_desc",
            "limit": limit,
            "offset": offset,
        }

        response = requests.get(
            f"{self.BASE_URL}/orders/search",
            headers=self._headers(),
            params=params,
            timeout=30,
        )

        if response.status_code >= 400:
            raise ValueError(
                f"Error consultando órdenes ML: {response.status_code} - {response.text}"
            )

        return response.json()

    def get_all_orders_by_seller(
        self,
        days: int = 30,
        limit: int = 50,
        max_pages: int = 20,
    ):
        me = self.get_me()
        seller_id = str(me["id"])

        all_orders = []

        for page in range(max_pages):
            offset = page * limit

            data = self.get_orders_by_seller(
                seller_id=seller_id,
                days=days,
                limit=limit,
                offset=offset,
            )

            results = data.get("results", [])

            if not results:
                break

            all_orders.extend(results)

            paging = data.get("paging", {})
            total = paging.get("total", 0)

            if offset + limit >= total:
                break

        return all_orders