from pydantic import BaseModel
from typing import Optional, List


class PublicationResponse(BaseModel):
    publication_id: str
    title: str

    thumbnail: Optional[str] = None
    permalink: Optional[str] = None

    price: Optional[float] = 0

    status: Optional[str] = None
    category_id: Optional[str] = None

    listing_type_id: Optional[str] = None
    currency_id: Optional[str] = "CLP"

    shipping_mode: Optional[str] = None
    logistic_type: Optional[str] = None
    free_shipping: Optional[bool] = False

    current_description: Optional[str] = ""

    active_description_type: Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedPublicationsResponse(BaseModel):
    items: List[PublicationResponse]

    page: int
    limit: int

    total: int
    total_pages: int


class SyncPublicationsResponse(BaseModel):
    message: str
    total_synced: int