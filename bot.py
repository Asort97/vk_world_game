from __future__ import annotations

import json
import random
from typing import Any

import vk_api
from vk_api.exceptions import ApiError
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

from config import settings


START_WORDS = {"начать", "старт", "start", "/start", "игра", "начать игру"}


def make_start_keyboard() -> str:
    if settings.vk_app_id and settings.vk_app_owner_id:
        button: dict[str, Any] = {
            "action": {
            "type": "open_app",
            "app_id": settings.vk_app_id,
            "owner_id": settings.vk_app_owner_id,
            "label": "Начать игру",
            "hash": "start",
            }
        }
    else:
        button = {
            "action": {
                "type": "open_link",
                "link": settings.mini_app_url,
                "label": "Начать игру",
            }
        }

    return json.dumps(
        {
            "one_time": False,
            "inline": False,
            "buttons": [[button]],
        },
        ensure_ascii=False,
    )


def send_message(api: Any, peer_id: int, text: str, keyboard: str | None = None) -> None:
    payload: dict[str, Any] = {
        "peer_id": peer_id,
        "message": text,
        "random_id": random.randint(1, 2_147_483_647),
    }
    if keyboard:
        payload["keyboard"] = keyboard
    api.messages.send(**payload)


def main() -> None:
    if not settings.vk_group_token:
        raise RuntimeError("VK_GROUP_TOKEN is empty. Fill .env first.")
    if not settings.vk_group_id:
        raise RuntimeError("VK_GROUP_ID is empty. Fill .env first.")

    vk_session = vk_api.VkApi(token=settings.vk_group_token, api_version=settings.vk_api_version)
    api = vk_session.get_api()
    try:
        longpoll = VkBotLongPoll(vk_session, settings.vk_group_id)
    except ApiError as error:
        if error.code == 15:
            raise RuntimeError(
                "VK denied Long Poll access. Create a new community access key "
                "with both permissions: 'Сообщения сообщества' and "
                "'Управление сообществом'. Also check that Long Poll API is enabled "
                "for the same community as VK_GROUP_ID."
            ) from error
        raise
    keyboard = make_start_keyboard()

    print("VK bot started")
    for event in longpoll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        message = event.object.message
        text = message.get("text", "").strip().lower()
        peer_id = message["peer_id"]

        if text in START_WORDS or not text:
            send_message(
                api,
                peer_id,
                "Привет! Нажми кнопку, чтобы открыть игру «Вокруг света за 80 дней».",
                keyboard,
            )
        else:
            send_message(
                api,
                peer_id,
                "Чтобы начать путешествие, нажми кнопку «Начать игру».",
                keyboard,
            )


if __name__ == "__main__":
    main()
