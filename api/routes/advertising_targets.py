from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db

from domain.services.advertising_target_service import (
    AdvertisingTargetService,
)

from schemas.advertising_target_schema import (
    AdvertisingTargetUpsertRequest,
    AdvertisingTargetResponse,
)

advertising_targets_router = APIRouter(
    prefix="/advertising-targets",
    tags=["Advertising Targets"],
)


@advertising_targets_router.put(
    "/{publication_id}",
    response_model=AdvertisingTargetResponse,
)
def upsert_advertising_target(
    publication_id: str,
    payload: AdvertisingTargetUpsertRequest,
    db: Session = Depends(get_db),
):
    service = AdvertisingTargetService(db)

    return service.upsert_target(
        publication_id=publication_id,
        target_acos=payload.target_acos,
        notes=payload.notes or "",
    )


@advertising_targets_router.get(
    "/{publication_id}",
    response_model=AdvertisingTargetResponse,
)
def get_advertising_target(
    publication_id: str,
    db: Session = Depends(get_db),
):
    service = AdvertisingTargetService(db)

    return service.get_target_by_publication(
        publication_id=publication_id,
    )