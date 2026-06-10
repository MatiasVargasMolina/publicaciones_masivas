from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
)

from sqlalchemy.orm import Session

from domain.services.description_service import (
    DescriptionService,
)

from domain.services.publication_service import (
    PublicationService,
)

from infrastructure.database.connection import (
    get_db,
)

from infrastructure.mercadolibre.oauth.token_storage import (
    obtener_access_token,
)

from schemas.description_schema import (
    DescriptionVariantRequest,
    DescriptionStatusRequest,
    DescriptionVariantResponse,
    ActiveDescriptionRequest,
)

router = APIRouter(
    prefix="/descriptions",
    tags=["Descriptions"],
)

description_service = DescriptionService()
publication_service = PublicationService()


@router.get("/base")
def get_base_descriptions(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    search: str | None = Query(None),

    db: Session = Depends(get_db),
):
    return publication_service.get_paginated_publications(
        db=db,
        page=page,
        limit=limit,
        search=search,
    )


@router.get("/meli-base")
def get_base_descriptions_from_meli():
    access_token = obtener_access_token()

    service = DescriptionService(
        access_token
    )

    return service.get_base_publications_with_details()


@router.get(
    "/variants",
    response_model=list[
        DescriptionVariantResponse
    ],
)
def get_variants(
    db: Session = Depends(get_db),
):
    return description_service.get_all_variants(
        db
    )


@router.put(
    "/variants",
    response_model=DescriptionVariantResponse,
)
def save_variant(
    request: DescriptionVariantRequest,
    db: Session = Depends(get_db),
):
    return description_service.save_variant(
        db,
        request,
    )


@router.patch(
    "/variants/status",
    response_model=DescriptionVariantResponse,
)
def update_variant_status(
    request: DescriptionStatusRequest,
    db: Session = Depends(get_db),
):
    return description_service.update_status(
        db,
        request,
    )


@router.patch("/active")
def set_active_description(
    request: ActiveDescriptionRequest,
    db: Session = Depends(get_db),
):
    try:
        return (
            description_service
            .set_active_description(
                db,
                request,
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )