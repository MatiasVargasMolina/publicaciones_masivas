from sqlalchemy.orm import Session

from infrastructure.database.models import (
    DescriptionVariantEntity,
    MeliPublicationEntity,
)

from schemas.description_schema import (
    DescriptionVariantRequest,
    DescriptionStatusRequest,
    ActiveDescriptionRequest,
)


class DescriptionService:
    def get_all_variants(
        self,
        db: Session,
    ):
        return db.query(
            DescriptionVariantEntity
        ).all()

    def save_variant(
        self,
        db: Session,
        request: DescriptionVariantRequest,
    ):
        variant = (
            db.query(DescriptionVariantEntity)
            .filter(
                DescriptionVariantEntity.publication_id
                == request.publication_id,

                DescriptionVariantEntity.variant_type
                == request.variant_type,
            )
            .first()
        )

        if variant:
            variant.text = request.text
            variant.status = request.status

        else:
            variant = DescriptionVariantEntity(
                publication_id=request.publication_id,
                variant_type=request.variant_type,
                text=request.text,
                status=request.status,
            )

            db.add(variant)

        db.commit()
        db.refresh(variant)

        return variant

    def update_status(
        self,
        db: Session,
        request: DescriptionStatusRequest,
    ):
        variant = (
            db.query(DescriptionVariantEntity)
            .filter(
                DescriptionVariantEntity.publication_id
                == request.publication_id,

                DescriptionVariantEntity.variant_type
                == request.variant_type,
            )
            .first()
        )

        if not variant:
            variant = DescriptionVariantEntity(
                publication_id=request.publication_id,
                variant_type=request.variant_type,
                text="",
                status=request.status,
            )

            db.add(variant)

        else:
            variant.status = request.status

        db.commit()
        db.refresh(variant)

        return variant

    def set_active_description(
        self,
        db: Session,
        request: ActiveDescriptionRequest,
    ):
        publication = (
            db.query(MeliPublicationEntity)
            .filter(
                MeliPublicationEntity.publication_id
                == request.publication_id
            )
            .first()
        )

        if not publication:
            raise ValueError(
                "Publicación no encontrada"
            )

        publication.active_description_type = (
            request.active_description_type
        )

        db.commit()
        db.refresh(publication)

        return {
            "publication_id":
                publication.publication_id,

            "active_description_type":
                publication.active_description_type,
        }