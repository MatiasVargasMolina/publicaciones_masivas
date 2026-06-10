from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from infrastructure.database.connection import get_db
from domain.services.kit_cost_service import KitCostService

router = APIRouter(
    prefix="/kit-costs",
    tags=["Kit Costs"],
)


@router.post("/calculate")
def calculate_kit_costs(db: Session = Depends(get_db)):
    service = KitCostService(db)
    return service.calculate_kit_costs()