from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def optional_int(name: str) -> int | None:
    value = os.getenv(name, "").strip()
    return int(value) if value else None


@dataclass(frozen=True)
class Settings:
    vk_group_token: str = os.getenv("VK_GROUP_TOKEN", "").strip()
    vk_group_id: int | None = optional_int("VK_GROUP_ID")
    vk_api_version: str = os.getenv("VK_API_VERSION", "5.199").strip()
    mini_app_url: str = os.getenv("MINI_APP_URL", "http://127.0.0.1:8000").strip()
    vk_app_id: int | None = optional_int("VK_APP_ID")
    vk_app_owner_id: int | None = optional_int("VK_APP_OWNER_ID")
    host: str = os.getenv("HOST", "127.0.0.1").strip()
    port: int = optional_int("PORT") or 8000


settings = Settings()
