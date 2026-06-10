# domain/services/pricing_service.py

from infrastructure.database.models import (
    ProductCostEntity,
    MeliPublicationEntity,
)


class PricingService:
    def calculate_cost_summary(
        self,
        publication: MeliPublicationEntity,
        cost: ProductCostEntity,
    ):
        sale_price = publication.price or 0

        direct_cost_after_discount = (
            cost.direct_purchase_cost
            * (1 - cost.direct_discount_percent / 100)
        )

        direct_final_unit_cost = (
            direct_cost_after_discount
            + cost.direct_shipping_cost
        )

        total_stock = (
            cost.disassembly_stock
            + cost.direct_stock
        )

        if total_stock > 0:
            average_unit_cost = (
                (
                    cost.disassembly_stock
                    * cost.disassembly_unit_cost
                )
                + (
                    cost.direct_stock
                    * direct_final_unit_cost
                )
            ) / total_stock
        else:
            average_unit_cost = 0

        margin_without_ads = (
            sale_price - average_unit_cost
        )

        margin_percent_without_ads = (
            (margin_without_ads / sale_price) * 100
            if sale_price > 0
            else 0
        )

        return {
            "publication_id": publication.publication_id,
            "title": publication.title,
            "thumbnail": publication.thumbnail,
            "sale_price": sale_price,

            "disassembly_stock": cost.disassembly_stock,
            "disassembly_unit_cost": cost.disassembly_unit_cost,

            "direct_stock": cost.direct_stock,
            "direct_purchase_cost": cost.direct_purchase_cost,
            "direct_discount_percent": cost.direct_discount_percent,
            "direct_shipping_cost": cost.direct_shipping_cost,

            "direct_final_unit_cost": round(
                direct_final_unit_cost,
                2,
            ),

            "average_unit_cost": round(
                average_unit_cost,
                2,
            ),

            "margin_without_ads": round(
                margin_without_ads,
                2,
            ),

            "margin_percent_without_ads": round(
                margin_percent_without_ads,
                2,
            ),
        }

    def get_margin_status(
        self,
        margin_percent_without_ads: float,
    ):
        if margin_percent_without_ads >= 50:
            return "EXCELENTE"

        if margin_percent_without_ads >= 35:
            return "BUENO"

        if margin_percent_without_ads >= 20:
            return "AJUSTADO"

        return "RIESGOSO"