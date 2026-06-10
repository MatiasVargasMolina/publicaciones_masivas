import traceback
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db
from domain.services.profitability_service import ProfitabilityService


router = APIRouter(
    prefix="/profitability",
    tags=["Profitability"],
)

service = ProfitabilityService()


@router.get("")
def get_all_profitability(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        return service.get_all_profitability(
            db=db,
            page=page,
            limit=limit,
        )

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/refresh")
def refresh_all_profitability(
    db: Session = Depends(get_db),
):
    try:
        return service.refresh_all_profitability(
            db=db,
        )

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )