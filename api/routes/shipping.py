from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db
from infrastructure.mercadolibre.oauth.token_storage import obtener_access_token

from domain.services.shipping_service import ShippingService


router = APIRouter(
    prefix="/shipping",
    tags=["Shipping"]
)


def get_access_token():
    access_token = obtener_access_token()

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No existe access_token. Debes autenticarte con MercadoLibre."
        )

    return access_token


@router.get("/free/{publication_id}")
def get_free_shipping_cost(
    publication_id: str,
    db: Session = Depends(get_db),
):
    try:
        service = ShippingService(get_access_token())

        return service.get_free_shipping_cost(
            db=db,
            publication_id=publication_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )