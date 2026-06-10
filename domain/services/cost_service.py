from sqlalchemy.orm import Session

from infrastructure.database.models import (
    MeliPublicationEntity,
    MarketplaceCostEntity,
)

from infrastructure.mercadolibre.listing_prices_client import ListingPricesClient
from infrastructure.mercadolibre.shipping_client import ShippingClient


class CostService:
    def __init__(self, access_token: str):
        self.listing_client = ListingPricesClient(access_token)
        self.shipping_client = ShippingClient(access_token)

    def get_all_costs(
        self,
        db: Session,
        page: int = 1,
        limit: int = 30,
    ):
        page = max(page, 1)
        limit = min(max(limit, 1), 100)

        query = db.query(MeliPublicationEntity)

        total = query.count()

        publications = (
            query
            .order_by(MeliPublicationEntity.updated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        items = []

        for publication in publications:
            saved_cost = (
                db.query(MarketplaceCostEntity)
                .filter(
                    MarketplaceCostEntity.publication_id
                    == publication.publication_id
                )
                .first()
            )

            items.append(
                self._build_cost_response(
                    publication=publication,
                    saved_cost=saved_cost,
                )
            )

        total_pages = (total + limit - 1) // limit if total > 0 else 1

        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        }

    def refresh_all_costs(
        self,
        db: Session,
    ):
        publications = db.query(MeliPublicationEntity).all()

        total_publications = len(publications)

        print("\n========== REFRESH ALL COSTS ==========")
        print("TOTAL PUBLICACIONES EN TABLA meli_publications:", total_publications)

        user_id = self.shipping_client.get_user_id()

        total_updated = 0
        errors = []

        for index, publication in enumerate(publications, start=1):
            try:
                print(
                    f"[{index}/{total_publications}] "
                    f"Actualizando {publication.publication_id}"
                )

                saved_cost = self._refresh_one_cost(
                    db=db,
                    publication=publication,
                    user_id=user_id,
                )

                db.commit()
                db.refresh(saved_cost)

                total_updated += 1

            except Exception as e:
                db.rollback()

                print(f"ERROR {publication.publication_id}: {str(e)}")

                errors.append(
                    {
                        "publication_id": publication.publication_id,
                        "title": publication.title,
                        "error": str(e),
                    }
                )

        print("TOTAL ACTUALIZADAS:", total_updated)
        print("TOTAL ERRORES:", len(errors))
        print("========== FIN REFRESH ALL COSTS ==========\n")

        return {
            "message": "Costos actualizados",
            "total_publications": total_publications,
            "total_updated": total_updated,
            "total_errors": len(errors),
            "errors": errors,
        }

    def _refresh_one_cost(
        self,
        db: Session,
        publication: MeliPublicationEntity,
        user_id: int,
    ):
        if publication.price is None:
            raise Exception(
                f"{publication.publication_id} no tiene price"
            )

        if not publication.category_id:
            raise Exception(
                f"{publication.publication_id} no tiene category_id"
            )

        listing_type_id = publication.listing_type_id or "gold_special"
        currency_id = publication.currency_id or "CLP"
        price = float(publication.price)

        listing_response = self.listing_client.get_listing_prices(
            site_id="MLC",
            price=price,
            category_id=publication.category_id,
            listing_type_id=listing_type_id,
            currency_id=currency_id,
        )

        if isinstance(listing_response, list):
            if not listing_response:
                raise Exception(
                    f"MercadoLibre no devolvió costos para "
                    f"{publication.publication_id}"
                )

            listing_data = listing_response[0]
        else:
            listing_data = listing_response

        sale_fee_details = listing_data.get("sale_fee_details") or {}

        sale_fee_amount = float(listing_data.get("sale_fee_amount") or 0)
        listing_fee_amount = float(listing_data.get("listing_fee_amount") or 0)
        percentage_fee = float(sale_fee_details.get("percentage_fee") or 0)

        total_meli_cost = sale_fee_amount + listing_fee_amount

        shipping_mode = publication.shipping_mode
        logistic_type = publication.logistic_type

        shipping_list_cost = 0
        shipping_seller_cost = 0
        billable_weight = 0

        should_calculate_shipping = (
            shipping_mode == "me2"
            and logistic_type != "custom"
        )

        if should_calculate_shipping:
            shipping_response = self.shipping_client.get_free_shipping_options(
                user_id=user_id,
                publication_id=publication.publication_id,
            )

            all_country = (
                shipping_response
                .get("coverage", {})
                .get("all_country", {})
            )

            shipping_list_cost = float(all_country.get("list_cost") or 0)
            billable_weight = float(all_country.get("billable_weight") or 0)
            shipping_seller_cost = shipping_list_cost
        else:
            print(
                f"OMITIENDO ENVÍO {publication.publication_id} "
                f"shipping_mode={shipping_mode} logistic_type={logistic_type}"
            )

        total_marketplace_cost = total_meli_cost + shipping_seller_cost

        saved_cost = (
            db.query(MarketplaceCostEntity)
            .filter(
                MarketplaceCostEntity.publication_id
                == publication.publication_id
            )
            .first()
        )

        if not saved_cost:
            saved_cost = MarketplaceCostEntity(
                publication_id=publication.publication_id,
            )

            db.add(saved_cost)

        saved_cost.sale_fee_amount = sale_fee_amount
        saved_cost.listing_fee_amount = listing_fee_amount
        saved_cost.total_meli_cost = total_meli_cost
        saved_cost.percentage_fee = percentage_fee

        saved_cost.shipping_list_cost = shipping_list_cost
        saved_cost.shipping_seller_cost = shipping_seller_cost
        saved_cost.billable_weight = billable_weight

        saved_cost.total_marketplace_cost = total_marketplace_cost
        saved_cost.currency_id = currency_id

        return saved_cost

    def _build_cost_response(
        self,
        publication: MeliPublicationEntity,
        saved_cost: MarketplaceCostEntity | None,
    ):
        price = float(publication.price or 0)

        if not saved_cost:
            return {
                "publication_id": publication.publication_id,
                "title": publication.title,
                "thumbnail": publication.thumbnail,
                "permalink": publication.permalink,

                "price": price,
                "category_id": publication.category_id,
                "listing_type_id": publication.listing_type_id,
                "currency_id": publication.currency_id or "CLP",

                "sale_fee_amount": 0,
                "listing_fee_amount": 0,
                "total_meli_cost": 0,
                "percentage_fee": 0,

                "shipping_list_cost": 0,
                "shipping_seller_cost": 0,
                "billable_weight": 0,

                "total_marketplace_cost": 0,
                "marketplace_cost_percent": 0,

                "has_cost": False,
                "updated_at": None,
            }

        total_marketplace_cost = float(saved_cost.total_marketplace_cost or 0)

        marketplace_cost_percent = 0

        if price > 0:
            marketplace_cost_percent = round(
                (total_marketplace_cost / price) * 100,
                2,
            )

        return {
            "publication_id": publication.publication_id,
            "title": publication.title,
            "thumbnail": publication.thumbnail,
            "permalink": publication.permalink,

            "price": price,
            "category_id": publication.category_id,
            "listing_type_id": publication.listing_type_id,
            "currency_id": saved_cost.currency_id,

            "sale_fee_amount": saved_cost.sale_fee_amount,
            "listing_fee_amount": saved_cost.listing_fee_amount,
            "total_meli_cost": saved_cost.total_meli_cost,
            "percentage_fee": saved_cost.percentage_fee,

            "shipping_list_cost": saved_cost.shipping_list_cost,
            "shipping_seller_cost": saved_cost.shipping_seller_cost,
            "billable_weight": saved_cost.billable_weight,

            "total_marketplace_cost": saved_cost.total_marketplace_cost,
            "marketplace_cost_percent": marketplace_cost_percent,

            "has_cost": True,
            "updated_at": saved_cost.updated_at,
        }