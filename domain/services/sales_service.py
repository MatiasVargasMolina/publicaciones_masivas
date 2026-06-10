from datetime import datetime

from infrastructure.database.models import PublicationSaleEntity


class SalesService:
    def __init__(self, db, sales_client):
        self.db = db
        self.sales_client = sales_client

    def sync_sales_by_seller(self, days: int = 30):
        orders = self.sales_client.get_all_orders_by_seller(
            days=days,
        )

        created_sales = 0
        skipped_sales = 0

        for order in orders:
            order_id = str(order.get("id"))
            status = order.get("status")
            currency_id = order.get("currency_id", "CLP")
            date_created = order.get("date_created")

            if not order_id or not date_created:
                skipped_sales += 1
                continue

            sale_date = datetime.fromisoformat(
                date_created.replace("Z", "+00:00")
            )

            order_items = order.get("order_items", [])

            for item_data in order_items:
                item = item_data.get("item", {})
                publication_id = item.get("id")

                if not publication_id:
                    skipped_sales += 1
                    continue

                exists = (
                    self.db.query(PublicationSaleEntity)
                    .filter(PublicationSaleEntity.order_id == order_id)
                    .first()
                )

                if exists:
                    skipped_sales += 1
                    continue

                quantity = item_data.get("quantity", 0) or 0
                unit_price = item_data.get("unit_price", 0) or 0
                total_amount = quantity * unit_price

                sale = PublicationSaleEntity(
                    publication_id=publication_id,
                    order_id=order_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_amount=total_amount,
                    sale_date=sale_date,
                    status=status,
                    currency_id=currency_id,
                )

                self.db.add(sale)
                created_sales += 1

        self.db.commit()

        return {
            "message": "Ventas sincronizadas correctamente",
            "processed_orders": len(orders),
            "created_sales": created_sales,
            "skipped_sales": skipped_sales,
        }