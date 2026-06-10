from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session

import json
import os

from infrastructure.database.connection import get_db
from infrastructure.database.models import (
    MeliPublicationEntity,
    PublicationRelationBaseEntity,
    PublicationRelationComponentEntity,
    PublicationRelationKitEntity,
    PublicationRelationUnassignedKitEntity,
)

router = APIRouter(
    prefix="/publication-relations",
    tags=["Publication Relations"],
)

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "publication_relations.json")


class PublicationMiniDTO(BaseModel):
    id: str
    title: str
    thumbnail: Optional[str] = ""
    price: Optional[float] = 0
    permalink: Optional[str] = ""
    is_kit: Optional[bool] = False


class KitRelationDTO(PublicationMiniDTO):
    assigned_count: Optional[int] = 0
    required_assignments: Optional[int] = 2
    double_unit_same_product: Optional[bool] = False


class AssignedRelationDTO(BaseModel):
    base: PublicationMiniDTO
    components_count: Optional[int] = 0
    kits_count: Optional[int] = 0
    components: List[PublicationMiniDTO] = Field(default_factory=list)
    kits: List[KitRelationDTO] = Field(default_factory=list)


class UnassignedKitDTO(PublicationMiniDTO):
    reason: Optional[str] = ""


class PublicationSystemDTO(BaseModel):
    assigned: List[AssignedRelationDTO] = Field(default_factory=list)
    unassigned_kits: List[UnassignedKitDTO] = Field(default_factory=list)
    double_unit_kit_ids: List[str] = Field(default_factory=list)


def mini_from_entity(entity):
    return {
        "id": entity.publication_id,
        "title": entity.title or "",
        "thumbnail": entity.thumbnail or "",
        "price": float(entity.price or 0),
        "permalink": entity.permalink or "",
        "is_kit": bool(entity.is_kit),
    }


def clear_relation_tables(db: Session):
    db.query(PublicationRelationComponentEntity).delete()
    db.query(PublicationRelationKitEntity).delete()
    db.query(PublicationRelationUnassignedKitEntity).delete()
    db.query(PublicationRelationBaseEntity).delete()
    db.commit()


def save_system_to_db(db: Session, system: dict):
    clear_relation_tables(db)

    for relation in system.get("assigned", []):
        base = relation.get("base")

        if not base or not base.get("id"):
            continue

        base_entity = PublicationRelationBaseEntity(
            publication_id=base.get("id"),
            title=base.get("title", ""),
            thumbnail=base.get("thumbnail", ""),
            price=base.get("price", 0),
            permalink=base.get("permalink", ""),
            is_kit=base.get("is_kit", False),
        )

        db.add(base_entity)

        for component in relation.get("components", []):
            if not component.get("id"):
                continue

            db.add(
                PublicationRelationComponentEntity(
                    base_publication_id=base.get("id"),
                    publication_id=component.get("id"),
                    title=component.get("title", ""),
                    thumbnail=component.get("thumbnail", ""),
                    price=component.get("price", 0),
                    permalink=component.get("permalink", ""),
                    is_kit=component.get("is_kit", False),
                )
            )

        for kit in relation.get("kits", []):
            if not kit.get("id"):
                continue

            db.add(
                PublicationRelationKitEntity(
                    base_publication_id=base.get("id"),
                    publication_id=kit.get("id"),
                    title=kit.get("title", ""),
                    thumbnail=kit.get("thumbnail", ""),
                    price=kit.get("price", 0),
                    permalink=kit.get("permalink", ""),
                    is_kit=True,
                    assigned_count=kit.get("assigned_count", 0),
                    required_assignments=kit.get("required_assignments", 2),
                    double_unit_same_product=kit.get("double_unit_same_product", False),
                )
            )

    for kit in system.get("unassigned_kits", []):
        if not kit.get("id"):
            continue

        db.add(
            PublicationRelationUnassignedKitEntity(
                publication_id=kit.get("id"),
                title=kit.get("title", ""),
                thumbnail=kit.get("thumbnail", ""),
                price=kit.get("price", 0),
                permalink=kit.get("permalink", ""),
                is_kit=True,
                reason=kit.get("reason", ""),
            )
        )

    db.commit()


def load_system_from_db(db: Session):
    bases = db.query(PublicationRelationBaseEntity).all()

    assigned = []

    for base in bases:
        components = (
            db.query(PublicationRelationComponentEntity)
            .filter(PublicationRelationComponentEntity.base_publication_id == base.publication_id)
            .all()
        )

        kits = (
            db.query(PublicationRelationKitEntity)
            .filter(PublicationRelationKitEntity.base_publication_id == base.publication_id)
            .all()
        )

        assigned.append({
            "base": mini_from_entity(base),
            "components_count": len(components),
            "kits_count": len(kits),
            "components": [
                mini_from_entity(component)
                for component in components
            ],
            "kits": [
                {
                    **mini_from_entity(kit),
                    "assigned_count": kit.assigned_count or 0,
                    "required_assignments": kit.required_assignments or 2,
                    "double_unit_same_product": bool(kit.double_unit_same_product),
                }
                for kit in kits
            ],
        })

    unassigned = db.query(PublicationRelationUnassignedKitEntity).all()

    double_unit_kit_ids = [
        kit.publication_id
        for kit in db.query(PublicationRelationKitEntity)
        .filter(PublicationRelationKitEntity.double_unit_same_product == True)
        .all()
    ]

    return {
        "assigned": assigned,
        "unassigned_kits": [
            {
                **mini_from_entity(kit),
                "reason": kit.reason or "",
            }
            for kit in unassigned
        ],
        "double_unit_kit_ids": double_unit_kit_ids,
    }


def load_system_from_json_file():
    if not os.path.exists(DATA_FILE):
        return {
            "assigned": [],
            "unassigned_kits": [],
            "double_unit_kit_ids": [],
        }

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def detect_is_kit(title: str):
    value = title.lower()

    keywords = [
        "kit",
        "pack",
        "combo",
        "set",
        "juego",
        "x2",
        "x 2",
        "x3",
        "x 3",
        "x4",
        "x 4",
        "par",
        "pares",
    ]

    return any(keyword in value for keyword in keywords)


def publication_to_mini(pub: MeliPublicationEntity):
    return {
        "id": pub.publication_id,
        "title": pub.title or "",
        "thumbnail": pub.thumbnail or "",
        "price": float(pub.price or 0),
        "permalink": pub.permalink or "",
        "is_kit": detect_is_kit(pub.title or ""),
    }


def collect_existing_ids(system: dict):
    ids = set()

    for relation in system.get("assigned", []):
        base = relation.get("base")

        if base and base.get("id"):
            ids.add(base["id"])

        for component in relation.get("components", []):
            if component.get("id"):
                ids.add(component["id"])

        for kit in relation.get("kits", []):
            if kit.get("id"):
                ids.add(kit["id"])

    for kit in system.get("unassigned_kits", []):
        if kit.get("id"):
            ids.add(kit["id"])

    return ids


@router.post("/save-system")
def save_publication_system(
    system: PublicationSystemDTO,
    db: Session = Depends(get_db),
):
    try:
        system_dict = system.model_dump()

        save_system_to_db(db, system_dict)

        return {
            "message": "Sistema de relaciones guardado en PostgreSQL correctamente",
            "assigned_count": len(system.assigned),
            "unassigned_kits_count": len(system.unassigned_kits),
            "double_unit_kits_count": len(system.double_unit_kit_ids),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar sistema de relaciones en BD: {str(e)}",
        )


@router.get("/system")
def get_publication_system(
    db: Session = Depends(get_db),
):
    try:
        return load_system_from_db(db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al leer sistema de relaciones desde BD: {str(e)}",
        )


@router.post("/import-json-to-db")
def import_json_to_db(
    db: Session = Depends(get_db),
):
    try:
        system = load_system_from_json_file()

        save_system_to_db(db, system)

        return {
            "message": "JSON migrado correctamente a PostgreSQL",
            "assigned_count": len(system.get("assigned", [])),
            "unassigned_kits_count": len(system.get("unassigned_kits", [])),
            "double_unit_kits_count": len(system.get("double_unit_kit_ids", [])),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al migrar JSON a BD: {str(e)}",
        )


@router.post("/sync-with-publications")
def sync_with_publications(
    db: Session = Depends(get_db),
):
    try:
        system = load_system_from_db(db)

        existing_ids = collect_existing_ids(system)

        publications = db.query(MeliPublicationEntity).all()

        added_bases = 0
        added_kits = 0

        assigned = system.get("assigned", [])
        unassigned_kits = system.get("unassigned_kits", [])

        for pub in publications:
            if pub.publication_id in existing_ids:
                continue

            mini = publication_to_mini(pub)

            if mini["is_kit"]:
                unassigned_kits.append({
                    **mini,
                    "reason": "Kit nuevo detectado desde publicaciones sincronizadas",
                })

                added_kits += 1

            else:
                assigned.append({
                    "base": mini,
                    "components_count": 0,
                    "kits_count": 0,
                    "components": [],
                    "kits": [],
                })

                added_bases += 1

            existing_ids.add(pub.publication_id)

        updated_system = {
            "assigned": assigned,
            "unassigned_kits": unassigned_kits,
            "double_unit_kit_ids": system.get("double_unit_kit_ids", []),
        }

        save_system_to_db(db, updated_system)

        return {
            "message": "Sistema sincronizado con publicaciones guardadas",
            "added_bases": added_bases,
            "added_kits": added_kits,
            "assigned_count": len(updated_system["assigned"]),
            "unassigned_kits_count": len(updated_system["unassigned_kits"]),
            "system": updated_system,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al sincronizar sistema con publicaciones: {str(e)}",
        )