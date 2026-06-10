from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from infrastructure.mercadolibre.oauth.config import MELI_CLIENT_ID, MELI_REDIRECT_URI
from infrastructure.mercadolibre.oauth.service import obtener_tokens_desde_codigo

router = APIRouter(prefix="/meli/oauth", tags=["MercadoLibre OAuth"])


@router.get("/login")
def login_meli():
    url = (
        "https://auth.mercadolibre.cl/authorization"
        f"?response_type=code"
        f"&client_id={MELI_CLIENT_ID}"
        f"&redirect_uri={MELI_REDIRECT_URI}"
    )

    return RedirectResponse(url)


@router.get("/callback")
def callback_meli(code: str):
    return obtener_tokens_desde_codigo(code)