from datetime import datetime
from pydantic import BaseModel


class PublicationSaleResponse(BaseModel):
    id: int
    publication_id: str
    order_id: str
    quantity: int
    unit_price: float
    total_amount: float
    sale_date: datetime
    status: str | None = None
    currency_id: str | None = "CLP"

    class Config:
        from_attributes = True


class SyncSalesResponse(BaseModel):
    message: str
    processed_orders: int
    created_sales: int
    skipped_sales: int