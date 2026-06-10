from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db
from domain.services.publication_group_service import PublicationGroupService

router = APIRouter(
    prefix="/publication-groups",
    tags=["Publication Groups"]
)


@router.get("/by-price-margin")
def group_publications_by_price_margin(
    max_per_group: int = Query(default=10, ge=2, le=50),
    db: Session = Depends(get_db)
):
    service = PublicationGroupService(db)

    return service.group_by_price_and_margin(
        max_per_group=max_per_group
    )