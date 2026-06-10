from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db
from infrastructure.mercadolibre.oauth.token_storage import obtener_access_token

from domain.services.publication_service import PublicationService

from schemas.publication_schema import (
    PaginatedPublicationsResponse,
    PublicationResponse,
    SyncPublicationsResponse,
)

router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)

service = PublicationService()


@router.get("", response_model=PaginatedPublicationsResponse)
def get_publications(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return service.get_paginated_publications(
        db=db,
        page=page,
        limit=limit,
        search=search,
    )


@router.get("/{publication_id}", response_model=PublicationResponse)
def get_publication(
    publication_id: str,
    db: Session = Depends(get_db),
):
    publication = service.get_publication_by_id(db, publication_id)

    if not publication:
        raise HTTPException(
            status_code=404,
            detail="Publicación no encontrada"
        )

    return publication


@router.post("/sync", response_model=SyncPublicationsResponse)
def sync_publications(
    page_size: int = Query(30, ge=1, le=50),
    max_items: int | None = Query(None, ge=1),
    include_descriptions: bool = Query(True),
    db: Session = Depends(get_db),
):
    access_token = obtener_access_token()

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No existe access_token. Debes autenticarte con MercadoLibre."
        )

    total_synced = service.sync_publications_from_meli(
        db=db,
        access_token=access_token,
        page_size=page_size,
        max_items=max_items,
        include_descriptions=include_descriptions,
    )

    return {
        "message": "Sincronización completada",
        "total_synced": total_synced,
    }