import hashlib
import hmac
from typing import Any
from urllib.parse import quote


class FalabellaSignature:
    @staticmethod
    def generate(api_key: str, params: dict[str, Any]) -> str:
        params_without_signature = {
            key: value
            for key, value in params.items()
            if key != "Signature"
        }

        sorted_params = sorted(params_without_signature.items())

        query_string = "&".join(
            f"{quote(str(key), safe='')}={quote(str(value), safe='')}"
            for key, value in sorted_params
        )

        return hmac.new(
            api_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()