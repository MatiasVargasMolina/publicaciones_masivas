import math
import requests

from sqlalchemy.orm import Session
from sqlalchemy import or_

from infrastructure.database.models import MeliPublicationEntity


class PublicationService:
    def get_paginated_publications(
        self,
        db: Session,
        page: int = 1,
        limit: int = 30,
        search: str | None = None,
    ):
        page = max(page, 1)
        limit = min(max(limit, 1), 100)

        query = db.query(MeliPublicationEntity)

        if search:
            search_value = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    MeliPublicationEntity.title.ilike(search_value),
                    MeliPublicationEntity.publication_id.ilike(search_value),
                )
            )

        total = query.count()
        total_pages = math.ceil(total / limit) if total > 0 else 1

        items = (
            query
            .order_by(MeliPublicationEntity.updated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        }

    def get_publication_by_id(
        self,
        db: Session,
        publication_id: str,
    ):
        return (
            db.query(MeliPublicationEntity)
            .filter(MeliPublicationEntity.publication_id == publication_id)
            .first()
        )

    def upsert_publication(
        self,
        db: Session,
        item: dict,
        current_description: str = "",
    ):
        publication_id = item.get("id")

        if not publication_id:
            return None

        shipping = item.get("shipping") or {}

        publication = (
            db.query(MeliPublicationEntity)
            .filter(MeliPublicationEntity.publication_id == publication_id)
            .first()
        )

        if publication:
            publication.title = item.get("title", publication.title)
            publication.thumbnail = item.get("thumbnail", publication.thumbnail)
            publication.permalink = item.get("permalink", publication.permalink)
            publication.price = item.get("price", publication.price)
            publication.status = item.get("status", publication.status)
            publication.category_id = item.get("category_id", publication.category_id)

            publication.listing_type_id = item.get(
                "listing_type_id",
                publication.listing_type_id,
            )

            publication.currency_id = item.get(
                "currency_id",
                publication.currency_id or "CLP",
            )

            publication.shipping_mode = shipping.get(
                "mode",
                publication.shipping_mode,
            )

            publication.logistic_type = shipping.get(
                "logistic_type",
                publication.logistic_type,
            )

            publication.free_shipping = shipping.get(
                "free_shipping",
                publication.free_shipping or False,
            )

            publication.current_description = current_description

        else:
            publication = MeliPublicationEntity(
                publication_id=publication_id,
                title=item.get("title", ""),
                thumbnail=item.get("thumbnail", ""),
                permalink=item.get("permalink", ""),
                price=item.get("price", 0),
                status=item.get("status", ""),
                category_id=item.get("category_id", ""),

                listing_type_id=item.get("listing_type_id"),
                currency_id=item.get("currency_id", "CLP"),

                shipping_mode=shipping.get("mode"),
                logistic_type=shipping.get("logistic_type"),
                free_shipping=shipping.get("free_shipping", False),

                current_description=current_description,
            )

            db.add(publication)

        return publication

    def sync_publications_from_meli(
        self,
        db: Session,
        access_token: str,
        page_size: int = 50,
        max_items: int | None = None,
        include_descriptions: bool = True,
    ):
        user_id = self._get_user_id(access_token)

        offset = 0
        total_synced = 0

        while True:
            search_url = (
                f"https://api.mercadolibre.com/users/{user_id}/items/search"
                f"?limit={page_size}&offset={offset}"
            )

            response = requests.get(
                search_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=20,
            )

            response.raise_for_status()
            data = response.json()

            item_ids = data.get("results", [])

            if not item_ids:
                break

            details = self._get_items_details(
                access_token=access_token,
                item_ids=item_ids,
            )

            for detail in details:
                body = detail.get("body", {})

                if not body:
                    continue

                item_id = body.get("id")
                current_description = ""

                if include_descriptions and item_id:
                    current_description = self._get_item_description(
                        access_token=access_token,
                        item_id=item_id,
                    )

                self.upsert_publication(
                    db=db,
                    item=body,
                    current_description=current_description,
                )

                total_synced += 1

                if max_items and total_synced >= max_items:
                    db.commit()
                    return total_synced

            db.commit()

            paging = data.get("paging", {})
            total = paging.get("total", 0)

            offset += page_size

            if offset >= total:
                break

        return total_synced

    def _get_user_id(
        self,
        access_token: str,
    ):
        response = requests.get(
            "https://api.mercadolibre.com/users/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )

        response.raise_for_status()
        return response.json()["id"]

    def _get_items_details(
        self,
        access_token: str,
        item_ids: list[str],
    ):
        all_results = []
        chunk_size = 20

        for i in range(0, len(item_ids), chunk_size):
            chunk = item_ids[i:i + chunk_size]
            ids = ",".join(chunk)

            response = requests.get(
                f"https://api.mercadolibre.com/items?ids={ids}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=30,
            )

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                all_results.extend(data)

        return all_results

    def _get_item_description(
        self,
        access_token: str,
        item_id: str,
    ):
        response = requests.get(
            f"https://api.mercadolibre.com/items/{item_id}/description",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=10,
        )

        if response.status_code == 404:
            return ""

        response.raise_for_status()
        data = response.json()

        return data.get("plain_text", "")