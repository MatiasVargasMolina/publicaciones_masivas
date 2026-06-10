from pydantic import BaseModel
from typing import Optional


class BaseCostUpdateRequest(BaseModel):
    disassembly_stock: Optional[int] = None
    disassembly_unit_cost: Optional[float] = None

    direct_stock: Optional[int] = None
    direct_purchase_cost: Optional[float] = None
    direct_discount_percent: Optional[float] = None
    direct_shipping_cost: Optional[float] = None


class BaseCostResponse(BaseModel):
    publication_id: str
    title: str

    thumbnail: Optional[str] = None
    permalink: Optional[str] = None

    price: float

    disassembly_stock: Optional[int] = None
    disassembly_unit_cost: Optional[float] = None
    disassembly_total_cost: float

    direct_stock: Optional[int] = None
    direct_purchase_cost: Optional[float] = None
    direct_discount_percent: Optional[float] = None
    direct_shipping_cost: Optional[float] = None
    direct_unit_cost: float
    direct_total_cost: float

    selected_cost_type: str
    selected_unit_cost: Optional[float] = None

    is_disassembly_cost_configured: bool
    is_direct_cost_configured: bool