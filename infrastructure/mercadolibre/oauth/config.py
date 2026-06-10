import os
from dotenv import load_dotenv

load_dotenv()

MELI_CLIENT_ID = os.getenv("MELI_APP_ID")
MELI_CLIENT_SECRET = os.getenv("MELI_CLIENT_SECRET")
MELI_REDIRECT_URI = os.getenv("MELI_REDIRECT_URI")

MELI_AUTH_URL = "https://auth.mercadolibre.cl/authorization"
MELI_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"