from pydantic import BaseModel
from typing import Optional


class AdvertisingTargetUpsertRequest(BaseModel):
    target_acos: Optional[float] = None
    notes: Optional[str] = ""


class AdvertisingTargetResponse(BaseModel):
    publication_id: str

    target_acos: Optional[float] = None
    target_roas: Optional[float] = None

    notes: Optional[str] = ""

    class Config:
        from_attributes = True