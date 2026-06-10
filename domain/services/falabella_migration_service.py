from fastapi import HTTPException
from sqlalchemy.orm import Session

from infrastructure.falabella.falabella_client import FalabellaClient
from infrastructure.falabella.falabella_mapper import FalabellaMapper
from infrastructure.database.models import MeliPublicationEntity


class FalabellaMigrationService:
    def __init__(self, db: Session):
        self.db = db
        self.client = FalabellaClient()
        self.mapper = FalabellaMapper()

    def get_publication_or_fail(self, publication_id: str) -> MeliPublicationEntity:
        publication = (
            self.db.query(MeliPublicationEntity)
            .filter(MeliPublicationEntity.publication_id == publication_id)
            .first()
        )

        if not publication:
            raise HTTPException(
                status_code=404,
                detail="Publicación MercadoLibre no encontrada",
            )

        return publication

    def get_candidates(self, limit: int = 30):
        publications = (
            self.db.query(MeliPublicationEntity)
            .filter(MeliPublicationEntity.status == "active")
            .limit(limit)
            .all()
        )

        return [
            {
                "publication_id": p.publication_id,
                "title": p.title,
                "price": p.price,
                "thumbnail": p.thumbnail,
                "status": p.status,
                "category_id": p.category_id,
            }
            for p in publications
        ]

    def preview_payload(
        self,
        publication_id: str,
        falabella_category_id: str | None = None,
    ):
        publication = self.get_publication_or_fail(publication_id)

        missing_fields = []

        if not falabella_category_id:
            missing_fields.append("falabella_category_id")

        payload = None

        if falabella_category_id:
            payload = self.mapper.meli_publication_to_product_payload(
                publication=publication,
                falabella_category_id=falabella_category_id,
            )

        return {
            "publication_id": publication_id,
            "meli_category_id": publication.category_id,
            "ready": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "payload": payload,
        }

    async def send_publication(
        self,
        publication_id: str,
        falabella_category_id: str,
    ):
        publication = self.get_publication_or_fail(publication_id)

        payload = self.mapper.meli_publication_to_product_payload(
            publication=publication,
            falabella_category_id=falabella_category_id,
        )

        result = await self.client.create_product(payload)

        return {
            "message": "Publicación enviada a Falabella",
            "publication_id": publication_id,
            "falabella_category_id": falabella_category_id,
            "result": result,
        }

    async def get_category_tree(self):
        return await self.client.get_category_tree()

    async def get_category_attributes(self, category_id: str):
        return await self.client.get_category_attributes(category_id)

    async def get_feed_status(self, feed_id: str):
        return await self.client.get_feed_status(feed_id)