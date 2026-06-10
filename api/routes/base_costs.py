from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db

from domain.services.base_cost_service import BaseCostService

from schemas.base_cost_schema import (
    BaseCostUpdateRequest,
)


router = APIRouter(
    prefix="/base-costs",
    tags=["Base Costs"],
)

service = BaseCostService()


@router.get("")
def get_all_base_costs(
    db: Session = Depends(get_db),
):
    try:
        return service.get_all_base_costs(db=db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.put("/{publication_id}")
def update_base_cost(
    publication_id: str,
    data: BaseCostUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        return service.update_base_cost(
            db=db,
            publication_id=publication_id,
            data=data,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )