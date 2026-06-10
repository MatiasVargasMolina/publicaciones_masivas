from sqlalchemy.orm import Session

from infrastructure.database.models import MeliPublicationEntity
from infrastructure.mercadolibre.shipping_client import ShippingClient


class ShippingService:
    def __init__(self, access_token: str):
        self.client = ShippingClient(access_token)

    def get_free_shipping_cost(
        self,
        db: Session,
        publication_id: str,
    ):
        publication = (
            db.query(MeliPublicationEntity)
            .filter(MeliPublicationEntity.publication_id == publication_id)
            .first()
        )

        if not publication:
            raise Exception(f"No existe publicación: {publication_id}")

        user_id = self.client.get_user_id()

        response = self.client.get_free_shipping_options(
            user_id=user_id,
            publication_id=publication_id,
        )

        coverage = response.get("coverage", {})
        currency_id = response.get("currency_id")
        list_cost = float(response.get("list_cost") or 0)
        cost = float(response.get("cost") or 0)

        seller_shipping_cost = max(list_cost - cost, 0)

        return {
            "publication_id": publication.publication_id,
            "title": publication.title,
            "price": float(publication.price or 0),
            "user_id": user_id,
            "currency_id": currency_id,
            "cost": cost,
            "list_cost": list_cost,
            "seller_shipping_cost": seller_shipping_cost,
            "coverage": coverage,
            "raw_response": response,
        }