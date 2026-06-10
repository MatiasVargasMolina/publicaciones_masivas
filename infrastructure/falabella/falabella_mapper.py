from typing import Any


class FalabellaMapper:
    @staticmethod
    def meli_publication_to_product_payload(
        publication,
        falabella_category_id: str,
        brand: str = "Genérico",
        stock: int = 100,
    ) -> dict[str, Any]:

        price = int(publication.price or 0)
        seller_sku = publication.publication_id

        description = (
            publication.current_description
            if getattr(publication, "current_description", None)
            else publication.title
        )

        image = publication.thumbnail if publication.thumbnail else None

        payload = {
            "Product": {
                "SellerSku": seller_sku,
                "Name": publication.title[:255],
                "PrimaryCategory": falabella_category_id,
                "Description": description,
                "Brand": brand,
                "Price": price,
                "Quantity": stock,
                "ProductId": seller_sku,
                "ProductIdType": "SellerSku",
                "BusinessUnits": {
                    "BusinessUnit": [
                        {
                            "OperatorCode": "facl",
                            "Price": price,
                            "Stock": stock,
                            "Status": "active",
                        }
                    ]
                },
            }
        }

        if image:
            payload["Product"]["Images"] = {
                "Image": [image]
            }

        return payload