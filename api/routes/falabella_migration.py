from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db
from domain.services.falabella_migration_service import FalabellaMigrationService

falabella_migration_router = APIRouter(
    prefix="/falabella-migration",
    tags=["Falabella Migration"],
)


@falabella_migration_router.get("/candidates")
def get_candidates(
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = FalabellaMigrationService(db)
    return service.get_candidates(limit)


@falabella_migration_router.get("/preview/{publication_id}")
def preview_publication(
    publication_id: str,
    falabella_category_id: str | None = None,
    db: Session = Depends(get_db),
):
    service = FalabellaMigrationService(db)
    return service.preview_payload(
        publication_id=publication_id,
        falabella_category_id=falabella_category_id,
    )


@falabella_migration_router.post("/send/{publication_id}")
async def send_publication(
    publication_id: str,
    falabella_category_id: str,
    db: Session = Depends(get_db),
):
    service = FalabellaMigrationService(db)
    return await service.send_publication(
        publication_id=publication_id,
        falabella_category_id=falabella_category_id,
    )


@falabella_migration_router.get("/categories/tree")
async def get_category_tree(
    db: Session = Depends(get_db),
):
    service = FalabellaMigrationService(db)
    return await service.get_category_tree()


@falabella_migration_router.get("/categories/{category_id}/attributes")
async def get_category_attributes(
    category_id: str,
    db: Session = Depends(get_db),
):
    service = FalabellaMigrationService(db)
    return await service.get_category_attributes(category_id)


@falabella_migration_router.get("/feeds/{feed_id}/status")
async def get_feed_status(
    feed_id: str,
    db: Session = Depends(get_db),
):
    service = FalabellaMigrationService(db)
    return await service.get_feed_status(feed_id)