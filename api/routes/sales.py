from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db
from infrastructure.mercadolibre.sales_client import MercadoLibreSalesClient
from domain.services.sales_service import SalesService
from schemas.sale_schema import SyncSalesResponse, PublicationSaleResponse
from infrastructure.database.models import PublicationSaleEntity


router = APIRouter(
    prefix="/sales",
    tags=["Sales"],
)


@router.post("/sync", response_model=SyncSalesResponse)
def sync_sales(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    client = MercadoLibreSalesClient()
    service = SalesService(db=db, sales_client=client)

    return service.sync_sales_by_seller(
        days=days,
    )


@router.get("/{publication_id}", response_model=list[PublicationSaleResponse])
def get_sales_by_publication(
    publication_id: str,
    db: Session = Depends(get_db),
):
    return (
        db.query(PublicationSaleEntity)
        .filter(PublicationSaleEntity.publication_id == publication_id)
        .order_by(PublicationSaleEntity.sale_date.desc())
        .all()
    )