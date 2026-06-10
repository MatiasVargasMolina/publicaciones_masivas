from pydantic import BaseModel
from typing import Optional, Any


class CostSimulationRequest(BaseModel):
    site_id: str = "MLC"
    price: float
    category_id: Optional[str] = None
    listing_type_id: Optional[str] = None
    currency_id: Optional[str] = "CLP"
    logistic_type: Optional[str] = None
    quantity: Optional[int] = None
    product_cost: Optional[float] = None
    shipping_cost: Optional[float] = 0


class ListingPriceOptionDTO(BaseModel):
    currency_id: Optional[str]
    listing_type_id: Optional[str]
    listing_type_name: Optional[str]
    listing_exposure: Optional[str]
    listing_fee_amount: Optional[float]
    sale_fee_amount: Optional[float]
    percentage_fee: Optional[float]
    fixed_fee: Optional[float]
    financing_add_on_fee: Optional[float]
    meli_percentage_fee: Optional[float]
    requires_picture: Optional[bool]
    raw: Any


class CostResultDTO(BaseModel):
    price: float
    category_id: Optional[str]
    listing_type_id: Optional[str]
    sale_fee_amount: float
    listing_fee_amount: float
    shipping_cost: float
    product_cost: Optional[float]
    total_meli_cost: float
    total_cost: Optional[float]
    estimated_profit: Optional[float]
    margin_percent: Optional[float]
    detail: ListingPriceOptionDTO