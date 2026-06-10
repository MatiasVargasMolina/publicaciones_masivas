from infrastructure.database.models import PublicationAdvertisingTargetEntity


class AdvertisingTargetService:
    def __init__(self, db):
        self.db = db

    def calculate_target_roas(self, target_acos):
        if target_acos is None or target_acos <= 0:
            return None

        return 100 / target_acos

    def upsert_target(self, publication_id: str, target_acos: float | None, notes: str = ""):
        target = (
            self.db.query(PublicationAdvertisingTargetEntity)
            .filter(
                PublicationAdvertisingTargetEntity.publication_id == publication_id
            )
            .first()
        )

        if target:
            target.target_acos = target_acos
            target.notes = notes or ""
        else:
            target = PublicationAdvertisingTargetEntity(
                publication_id=publication_id,
                target_acos=target_acos,
                notes=notes or "",
            )
            self.db.add(target)

        self.db.commit()
        self.db.refresh(target)

        return {
            "publication_id": target.publication_id,
            "target_acos": target.target_acos,
            "target_roas": self.calculate_target_roas(target.target_acos),
            "notes": target.notes,
        }

    def get_target_by_publication(self, publication_id: str):
        target = (
            self.db.query(PublicationAdvertisingTargetEntity)
            .filter(
                PublicationAdvertisingTargetEntity.publication_id == publication_id
            )
            .first()
        )

        if not target:
            return {
                "publication_id": publication_id,
                "target_acos": None,
                "target_roas": None,
                "notes": "",
            }

        return {
            "publication_id": target.publication_id,
            "target_acos": target.target_acos,
            "target_roas": self.calculate_target_roas(target.target_acos),
            "notes": target.notes,
        }