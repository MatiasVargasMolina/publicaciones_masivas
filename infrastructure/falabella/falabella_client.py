from datetime import datetime, timezone
from typing import Any

import httpx

from core.config import settings
from infrastructure.falabella.falabella_signature import FalabellaSignature


class FalabellaClient:
    def __init__(self):
        self.api_url = settings.FALABELLA_API_URL
        self.user_id = settings.FALABELLA_USER_ID
        self.api_key = settings.FALABELLA_API_KEY
        self.version = settings.FALABELLA_VERSION
        self.format = settings.FALABELLA_FORMAT

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")

    def _build_params(self, action: str) -> dict[str, Any]:
        params = {
            "Action": action,
            "Format": self.format,
            "Timestamp": self._timestamp(),
            "UserID": self.user_id,
            "Version": self.version,
        }

        params["Signature"] = FalabellaSignature.generate(
            api_key=self.api_key,
            params=params,
        )

        return params

    async def get_category_tree(self) -> dict[str, Any]:
        return await self.get("GetCategoryTree")

    async def get_category_attributes(self, category_id: str) -> dict[str, Any]:
        return await self.get(
            action="GetCategoryAttributes",
            extra_params={"PrimaryCategory": category_id},
        )

    async def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.post(
            action="ProductCreate",
            payload=payload,
        )

    async def update_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.post(
            action="ProductUpdate",
            payload=payload,
        )

    async def get_feed_status(self, feed_id: str) -> dict[str, Any]:
        return await self.get(
            action="FeedStatus",
            extra_params={"FeedID": feed_id},
        )

    async def get(
        self,
        action: str,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = self._build_params(action)

        if extra_params:
            params.update(extra_params)
            params["Signature"] = FalabellaSignature.generate(
                api_key=self.api_key,
                params={k: v for k, v in params.items() if k != "Signature"},
            )

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                self.api_url,
                params=params,
                headers={"accept": "application/json"},
            )

        response.raise_for_status()
        return response.json()

    async def post(
        self,
        action: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        params = self._build_params(action)

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.api_url,
                params=params,
                json=payload,
                headers={
                    "accept": "application/json",
                    "content-type": "application/json",
                },
            )

        response.raise_for_status()
        return response.json()