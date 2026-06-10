from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db
from infrastructure.mercadolibre.oauth.token_storage import obtener_access_token

from domain.services.cost_service import CostService


router = APIRouter(
    prefix="/costs",
    tags=["Costs"],
)


def get_access_token():
    access_token = obtener_access_token()

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No existe access_token",
        )

    return access_token


@router.get("")
def get_all_costs(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        service = CostService(get_access_token())

        return service.get_all_costs(
            db=db,
            page=page,
            limit=limit,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/refresh")
def refresh_all_costs(
    db: Session = Depends(get_db),
):
    try:
        service = CostService(get_access_token())

        return service.refresh_all_costs(db=db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )