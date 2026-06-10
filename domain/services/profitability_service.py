from sqlalchemy.orm import Session
from sqlalchemy import or_

from infrastructure.database.models import (
    MeliPublicationEntity,
    ProductCostEntity,
    MarketplaceCostEntity,
    PublicationProfitabilityEntity,
)


class ProfitabilityService:
    def get_all_profitability(
        self,
        db: Session,
        page: int = 1,
        limit: int = 30,
    ):
        page = max(page, 1)
        limit = min(max(limit, 1), 100)

        query = (
            db.query(MeliPublicationEntity)
            .join(
                ProductCostEntity,
                ProductCostEntity.publication_id
                == MeliPublicationEntity.publication_id,
            )
            .filter(
                or_(
                    ProductCostEntity.disassembly_unit_cost > 0,
                    ProductCostEntity.direct_purchase_cost > 0,
                    ProductCostEntity.calculated_kit_product_cost > 0,
                )
            )
            .order_by(MeliPublicationEntity.updated_at.desc())
        )

        total = query.count()

        publications = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        items = []

        for publication in publications:
            profitability = (
                db.query(PublicationProfitabilityEntity)
                .filter(
                    PublicationProfitabilityEntity.publication_id
                    == publication.publication_id
                )
                .first()
            )

            items.append(
                self._build_response(
                    publication=publication,
                    profitability=profitability,
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

    def refresh_all_profitability(
        self,
        db: Session,
    ):
        publications = (
            db.query(MeliPublicationEntity)
            .join(
                ProductCostEntity,
                ProductCostEntity.publication_id
                == MeliPublicationEntity.publication_id,
            )
            .filter(
                or_(
                    ProductCostEntity.disassembly_unit_cost > 0,
                    ProductCostEntity.direct_purchase_cost > 0,
                    ProductCostEntity.calculated_kit_product_cost > 0,
                )
            )
            .all()
        )

        total_updated = 0
        errors = []

        print("\n========== REFRESH PROFITABILITY ==========")
        print("TOTAL PUBLICACIONES CON COSTO:", len(publications))

        for index, publication in enumerate(publications, start=1):
            try:
                print(
                    f"[{index}/{len(publications)}] "
                    f"Actualizando rentabilidad {publication.publication_id}"
                )

                profitability = self._refresh_one_profitability(
                    db=db,
                    publication=publication,
                )

                db.commit()
                db.refresh(profitability)

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
        print("========== FIN REFRESH PROFITABILITY ==========\n")

        return {
            "message": "Rentabilidad actualizada",
            "total_publications_with_cost": len(publications),
            "total_updated": total_updated,
            "total_errors": len(errors),
            "errors": errors,
        }

    def _refresh_one_profitability(
        self,
        db: Session,
        publication: MeliPublicationEntity,
    ):
        price = float(publication.price or 0)

        marketplace_cost = (
            db.query(MarketplaceCostEntity)
            .filter(
                MarketplaceCostEntity.publication_id
                == publication.publication_id
            )
            .first()
        )

        product_cost = (
            db.query(ProductCostEntity)
            .filter(
                ProductCostEntity.publication_id
                == publication.publication_id
            )
            .first()
        )

        sale_fee_amount = 0
        shipping_seller_cost = 0
        total_marketplace_cost = 0

        if marketplace_cost:
            sale_fee_amount = float(marketplace_cost.sale_fee_amount or 0)
            shipping_seller_cost = float(
                marketplace_cost.shipping_seller_cost or 0
            )
            total_marketplace_cost = float(
                marketplace_cost.total_marketplace_cost or 0
            )

        disassembly_unit_cost = 0
        direct_unit_cost = 0
        calculated_kit_product_cost = 0

        if product_cost:
            disassembly_unit_cost = float(
                product_cost.disassembly_unit_cost or 0
            )

            direct_unit_cost = float(
                product_cost.direct_purchase_cost or 0
            )

            calculated_kit_product_cost = float(
                product_cost.calculated_kit_product_cost or 0
            )

        # DESARME
        disassembly_total_cost = (
            disassembly_unit_cost +
            total_marketplace_cost
        )
        disassembly_profit = price - disassembly_total_cost
        disassembly_margin_percent = 0

        if price > 0:
            disassembly_margin_percent = round(
                (disassembly_profit / price) * 100,
                2,
            )

        # COMPRA DIRECTA
        direct_total_cost = (
            direct_unit_cost +
            total_marketplace_cost
        )
        direct_profit = price - direct_total_cost
        direct_margin_percent = 0

        if price > 0:
            direct_margin_percent = round(
                (direct_profit / price) * 100,
                2,
            )

        # KIT
        kit_total_cost = (
            calculated_kit_product_cost +
            total_marketplace_cost
        )
        kit_profit = price - kit_total_cost
        kit_margin_percent = 0

        if price > 0:
            kit_margin_percent = round(
                (kit_profit / price) * 100,
                2,
            )

        recommended_cost_type = "none"
        recommended_profit = 0
        recommended_margin_percent = 0

        has_disassembly_cost = disassembly_unit_cost > 0
        has_direct_cost = direct_unit_cost > 0
        has_kit_cost = calculated_kit_product_cost > 0

        options = []

        if has_disassembly_cost:
            options.append(
                {
                    "type": "disassembly",
                    "profit": disassembly_profit,
                    "margin": disassembly_margin_percent,
                }
            )

        if has_direct_cost:
            options.append(
                {
                    "type": "direct",
                    "profit": direct_profit,
                    "margin": direct_margin_percent,
                }
            )

        if has_kit_cost:
            options.append(
                {
                    "type": "kit",
                    "profit": kit_profit,
                    "margin": kit_margin_percent,
                }
            )

        if options:
            best = max(options, key=lambda item: item["margin"])

            recommended_cost_type = best["type"]
            recommended_profit = best["profit"]
            recommended_margin_percent = best["margin"]

        profitability = (
            db.query(PublicationProfitabilityEntity)
            .filter(
                PublicationProfitabilityEntity.publication_id
                == publication.publication_id
            )
            .first()
        )

        if not profitability:
            profitability = PublicationProfitabilityEntity(
                publication_id=publication.publication_id,
            )
            db.add(profitability)

        profitability.price = price

        profitability.sale_fee_amount = sale_fee_amount
        profitability.shipping_seller_cost = shipping_seller_cost
        profitability.total_marketplace_cost = total_marketplace_cost

        profitability.disassembly_unit_cost = disassembly_unit_cost
        profitability.disassembly_total_cost = disassembly_total_cost
        profitability.disassembly_profit = disassembly_profit
        profitability.disassembly_margin_percent = disassembly_margin_percent

        profitability.direct_unit_cost = direct_unit_cost
        profitability.direct_total_cost = direct_total_cost
        profitability.direct_profit = direct_profit
        profitability.direct_margin_percent = direct_margin_percent

        profitability.calculated_kit_product_cost = calculated_kit_product_cost
        profitability.kit_total_cost = kit_total_cost
        profitability.kit_profit = kit_profit
        profitability.kit_margin_percent = kit_margin_percent

        profitability.recommended_cost_type = recommended_cost_type
        profitability.recommended_profit = recommended_profit
        profitability.recommended_margin_percent = recommended_margin_percent

        return profitability

    def _build_response(
        self,
        publication: MeliPublicationEntity,
        profitability: PublicationProfitabilityEntity | None,
    ):
        if not profitability:
            return {
                "publication_id": publication.publication_id,
                "title": publication.title,
                "thumbnail": publication.thumbnail,
                "permalink": publication.permalink,

                "price": float(publication.price or 0),

                "sale_fee_amount": 0,
                "shipping_seller_cost": 0,
                "total_marketplace_cost": 0,

                "disassembly_unit_cost": 0,
                "disassembly_total_cost": 0,
                "disassembly_profit": 0,
                "disassembly_margin_percent": 0,

                "direct_unit_cost": 0,
                "direct_total_cost": 0,
                "direct_profit": 0,
                "direct_margin_percent": 0,

                "is_kit": False,
                "calculated_kit_product_cost": 0,
                "kit_total_cost": 0,
                "kit_profit": 0,
                "kit_margin_percent": 0,

                "recommended_cost_type": "none",
                "recommended_profit": 0,
                "recommended_margin_percent": 0,

                "has_profitability": False,
                "updated_at": None,
            }

        calculated_kit_product_cost = float(
            profitability.calculated_kit_product_cost or 0
        )

        return {
            "publication_id": publication.publication_id,
            "title": publication.title,
            "thumbnail": publication.thumbnail,
            "permalink": publication.permalink,

            "price": profitability.price,

            "sale_fee_amount": profitability.sale_fee_amount,
            "shipping_seller_cost": profitability.shipping_seller_cost,
            "total_marketplace_cost": profitability.total_marketplace_cost,

            "disassembly_unit_cost": profitability.disassembly_unit_cost,
            "disassembly_total_cost": profitability.disassembly_total_cost,
            "disassembly_profit": profitability.disassembly_profit,
            "disassembly_margin_percent": profitability.disassembly_margin_percent,

            "direct_unit_cost": profitability.direct_unit_cost,
            "direct_total_cost": profitability.direct_total_cost,
            "direct_profit": profitability.direct_profit,
            "direct_margin_percent": profitability.direct_margin_percent,

            "is_kit": calculated_kit_product_cost > 0,
            "calculated_kit_product_cost": calculated_kit_product_cost,
            "kit_total_cost": profitability.kit_total_cost or 0,
            "kit_profit": profitability.kit_profit or 0,
            "kit_margin_percent": profitability.kit_margin_percent or 0,

            "recommended_cost_type": profitability.recommended_cost_type,
            "recommended_profit": profitability.recommended_profit,
            "recommended_margin_percent": profitability.recommended_margin_percent,

            "has_profitability": True,
            "updated_at": profitability.updated_at,
        }