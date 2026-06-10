from sqlalchemy.orm import Session

from infrastructure.database.models import (
    ProductCostEntity,
    PublicationRelationBaseEntity,
)


class BaseCostService:
    def get_all_base_costs(self, db: Session):
        bases = (
            db.query(PublicationRelationBaseEntity)
            .order_by(PublicationRelationBaseEntity.updated_at.desc())
            .all()
        )

        result = []

        for base in bases:
            cost = self._get_or_empty_cost(
                db=db,
                publication_id=base.publication_id,
            )

            result.append(
                self._build_response(
                    base=base,
                    cost=cost,
                )
            )

        return {
            "items": result,
            "total": len(result),
        }

    def update_base_cost(
        self,
        db: Session,
        publication_id: str,
        data,
    ):
        base = (
            db.query(PublicationRelationBaseEntity)
            .filter(PublicationRelationBaseEntity.publication_id == publication_id)
            .first()
        )

        if not base:
            raise Exception(f"No existe publicación base: {publication_id}")

        cost = (
            db.query(ProductCostEntity)
            .filter(ProductCostEntity.publication_id == publication_id)
            .first()
        )

        if not cost:
            cost = ProductCostEntity(publication_id=publication_id)
            db.add(cost)

        # Stock puede quedar en 0 por defecto
        cost.disassembly_stock = data.disassembly_stock or 0
        cost.direct_stock = data.direct_stock or 0

        # Costos NO deben usar "or 0"
        # None = no configurado
        # 0 = configurado con costo cero
        cost.disassembly_unit_cost = data.disassembly_unit_cost
        cost.direct_purchase_cost = data.direct_purchase_cost
        cost.direct_discount_percent = data.direct_discount_percent
        cost.direct_shipping_cost = data.direct_shipping_cost

        db.commit()
        db.refresh(cost)

        return self._build_response(
            base=base,
            cost=cost,
        )

    def _get_or_empty_cost(
        self,
        db: Session,
        publication_id: str,
    ):
        cost = (
            db.query(ProductCostEntity)
            .filter(ProductCostEntity.publication_id == publication_id)
            .first()
        )

        if cost:
            return cost

        return ProductCostEntity(
            publication_id=publication_id,
            disassembly_stock=0,
            disassembly_unit_cost=None,
            direct_stock=0,
            direct_purchase_cost=None,
            direct_discount_percent=None,
            direct_shipping_cost=None,
        )

    def _build_response(
        self,
        base,
        cost,
    ):
        price = float(base.price or 0)

        disassembly_stock = int(cost.disassembly_stock or 0)

        disassembly_unit_cost = (
            float(cost.disassembly_unit_cost)
            if cost.disassembly_unit_cost is not None
            else None
        )

        disassembly_total_cost = (
            disassembly_stock * disassembly_unit_cost
            if disassembly_unit_cost is not None
            else None
        )

        direct_stock = int(cost.direct_stock or 0)

        direct_purchase_cost = (
            float(cost.direct_purchase_cost)
            if cost.direct_purchase_cost is not None
            else None
        )

        direct_discount_percent = (
            float(cost.direct_discount_percent)
            if cost.direct_discount_percent is not None
            else None
        )

        direct_shipping_cost = (
            float(cost.direct_shipping_cost)
            if cost.direct_shipping_cost is not None
            else None
        )

        is_direct_cost_configured = direct_purchase_cost is not None

        if is_direct_cost_configured:
            discount = direct_discount_percent or 0
            shipping = direct_shipping_cost or 0

            discount_amount = direct_purchase_cost * discount / 100
            direct_unit_cost = direct_purchase_cost - discount_amount + shipping
            direct_total_cost = direct_stock * direct_unit_cost
        else:
            direct_unit_cost = None
            direct_total_cost = None

        is_disassembly_cost_configured = disassembly_unit_cost is not None

        if is_direct_cost_configured and direct_stock > 0:
            selected_cost_type = "direct"
            selected_unit_cost = direct_unit_cost
        elif is_disassembly_cost_configured and disassembly_stock > 0:
            selected_cost_type = "disassembly"
            selected_unit_cost = disassembly_unit_cost
        else:
            selected_cost_type = "none"
            selected_unit_cost = None

        return {
            "publication_id": base.publication_id,
            "title": base.title,
            "thumbnail": base.thumbnail,
            "permalink": base.permalink,
            "price": price,

            "disassembly_stock": disassembly_stock,
            "disassembly_unit_cost": disassembly_unit_cost,
            "disassembly_total_cost": disassembly_total_cost,
            "is_disassembly_cost_configured": is_disassembly_cost_configured,

            "direct_stock": direct_stock,
            "direct_purchase_cost": direct_purchase_cost,
            "direct_discount_percent": direct_discount_percent,
            "direct_shipping_cost": direct_shipping_cost,
            "direct_unit_cost": direct_unit_cost,
            "direct_total_cost": direct_total_cost,
            "is_direct_cost_configured": is_direct_cost_configured,

            "selected_cost_type": selected_cost_type,
            "selected_unit_cost": selected_unit_cost,
        }