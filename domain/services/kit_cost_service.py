from collections import defaultdict

from infrastructure.database.models import (
    PublicationRelationKitEntity,
    ProductCostEntity,
)


class KitCostService:
    def __init__(self, db):
        self.db = db

    def _get_valid_min_cost(self, product_cost: ProductCostEntity):
        values = [
            product_cost.disassembly_unit_cost,
            product_cost.direct_purchase_cost,
        ]

        valid_values = [
            float(value)
            for value in values
            if value is not None and float(value) > 0
        ]

        if not valid_values:
            return None

        return min(valid_values)

    def calculate_kit_costs(self):
        relations = self.db.query(PublicationRelationKitEntity).all()

        kits_map = defaultdict(list)

        for relation in relations:
            kit_id = str(relation.publication_id).strip()
            base_id = str(relation.base_publication_id).strip()

            kits_map[kit_id].append(relation)

        updated = 0
        pending = 0
        created_kit_cost_rows = 0

        updated_kits = []
        pending_kits = []

        for kit_id, kit_relations in kits_map.items():
            total_kit_cost = 0
            components = []
            can_calculate = True

            for relation in kit_relations:
                base_id = str(relation.base_publication_id).strip()

                base_cost = (
                    self.db.query(ProductCostEntity)
                    .filter(ProductCostEntity.publication_id == base_id)
                    .first()
                )

                if not base_cost:
                    can_calculate = False
                    components.append({
                        "base_id": base_id,
                        "status": "pending",
                        "reason": "base_cost_not_found",
                    })
                    break

                selected_cost = self._get_valid_min_cost(base_cost)

                if selected_cost is None:
                    can_calculate = False
                    components.append({
                        "base_id": base_id,
                        "status": "pending",
                        "reason": "base_cost_zero_null_or_none",
                        "disassembly_unit_cost": base_cost.disassembly_unit_cost,
                        "direct_purchase_cost": base_cost.direct_purchase_cost,
                    })
                    break

                quantity = 2 if relation.double_unit_same_product else 1
                component_total = selected_cost * quantity

                total_kit_cost += component_total

                components.append({
                    "base_id": base_id,
                    "status": "ok",
                    "selected_unit_cost": selected_cost,
                    "quantity": quantity,
                    "component_total": component_total,
                    "disassembly_unit_cost": base_cost.disassembly_unit_cost,
                    "direct_purchase_cost": base_cost.direct_purchase_cost,
                })

            if not can_calculate:
                pending += 1
                pending_kits.append({
                    "kit_id": kit_id,
                    "reason": "kit_has_incomplete_base_costs",
                    "components": components,
                })
                continue

            kit_cost = (
                self.db.query(ProductCostEntity)
                .filter(ProductCostEntity.publication_id == kit_id)
                .first()
            )

            if not kit_cost:
                kit_cost = ProductCostEntity(
                    publication_id=kit_id,
                    disassembly_stock=0,
                    disassembly_unit_cost=0,
                    direct_stock=0,
                    direct_purchase_cost=0,
                    direct_discount_percent=0,
                    direct_shipping_cost=0,
                    calculated_kit_product_cost=None,
                )
                self.db.add(kit_cost)
                self.db.flush()
                created_kit_cost_rows += 1

            old_calculated_cost = kit_cost.calculated_kit_product_cost

            kit_cost.calculated_kit_product_cost = total_kit_cost

            # Importante:
            # NO tocar disassembly_unit_cost
            # NO tocar direct_purchase_cost
            # NO tocar direct_shipping_cost
            # NO tocar direct_discount_percent

            self.db.add(kit_cost)

            updated += 1
            updated_kits.append({
                "kit_id": kit_id,
                "old_calculated_kit_product_cost": old_calculated_cost,
                "new_calculated_kit_product_cost": total_kit_cost,
                "components_count": len(kit_relations),
                "components": components,
            })

        self.db.commit()

        return {
            "message": "Costos de kits calculados correctamente",
            "total_kits": len(kits_map),
            "updated": updated,
            "pending": pending,
            "created_kit_cost_rows": created_kit_cost_rows,
            "updated_kits": updated_kits[:100],
            "pending_kits": pending_kits[:100],
        }