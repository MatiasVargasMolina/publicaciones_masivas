from infrastructure.mercadolibre.oauth.client import exchange_code_for_token
from infrastructure.mercadolibre.oauth.token_storage import guardar_token


def obtener_tokens_desde_codigo(code: str) -> dict:
    token_data = exchange_code_for_token(code)

    guardar_token(token_data)

    return {
        "mensaje": "Token guardado correctamente",
        "token_type": token_data.get("token_type"),
        "expires_in": token_data.get("expires_in"),
        "user_id": token_data.get("user_id"),
    }