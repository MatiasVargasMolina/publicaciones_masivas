from typing import Literal

from pydantic import BaseModel


VariantType = Literal[
    "seo_tecnico",
    "compatibilidad",
    "conversion",
]

VariantStatus = Literal[
    "draft",
    "modified",
    "approved",
]


class DescriptionVariantRequest(BaseModel):
    publication_id: str
    variant_type: VariantType
    text: str
    status: VariantStatus


class DescriptionStatusRequest(BaseModel):
    publication_id: str
    variant_type: VariantType
    status: VariantStatus


class DescriptionVariantResponse(BaseModel):
    id: int
    publication_id: str
    variant_type: VariantType
    text: str
    status: VariantStatus

    class Config:
        from_attributes = True


class ActiveDescriptionRequest(BaseModel):
    publication_id: str
    active_description_type: VariantType