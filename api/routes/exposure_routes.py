from fastapi import APIRouter, HTTPException
from domain.services.exposure_service import ExposureService
from infrastructure.mercadolibre.oauth.token_storage import obtener_access_token

router = APIRouter(prefix="/exposures", tags=["Exposures"])

service = ExposureService()


def get_token_or_fail() -> str:
    token = obtener_access_token()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="No hay token guardado. Primero debes autenticar con MercadoLibre."
        )

    return token


@router.get("/{site_id}")
def get_exposures(site_id: str):
    token = get_token_or_fail()
    return service.get_all(site_id, token)


@router.get("/{site_id}/{exposure}")
def get_exposure(site_id: str, exposure: str):
    token = get_token_or_fail()
    return service.get_one(site_id, exposure, token)