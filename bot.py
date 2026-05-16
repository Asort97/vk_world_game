from __future__ import annotations

import json
import random
from typing import Any

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.exceptions import ApiError

from config import settings


START_COMMANDS = {"start"}
START_WORDS = {"начать", "старт", "start", "/start", "игра", "начать игру", "привет", "здравствуйте"}
YES_WORDS = {"да", "давай", "сыграть", "хочу", "хочу сыграть", "играть", "согласен", "согласна"}
NO_WORDS = {"нет", "не хочу", "потом", "отказ", "не сейчас"}


def payload(command: str) -> str:
    return json.dumps({"command": command}, ensure_ascii=False)


def make_offer_keyboard() -> str:
    return json.dumps(
        {
            "one_time": True,
            "inline": False,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "text",
                            "label": "Да, сыграть",
                            "payload": payload("play_yes"),
                        },
                        "color": "positive",
                    },
                    {
                        "action": {
                            "type": "text",
                            "label": "Нет",
                            "payload": payload("play_no"),
                        },
                        "color": "secondary",
                    },
                ]
            ],
        },
        ensure_ascii=False,
    )


def make_start_keyboard() -> str:
    app_link = f"https://vk.com/app{settings.vk_app_id}" if settings.vk_app_id else settings.mini_app_url
    return json.dumps(
        {
            "one_time": True,
            "inline": False,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "open_link",
                            "link": app_link,
                            "label": "Начать",
                        }
                    }
                ]
            ],
        },
        ensure_ascii=False,
    )


def make_empty_keyboard() -> str:
    return json.dumps({"one_time": True, "inline": False, "buttons": []}, ensure_ascii=False)


def send_message(api: Any, peer_id: int, text: str, keyboard: str | None = None) -> None:
    payload_data: dict[str, Any] = {
        "peer_id": peer_id,
        "message": text,
        "random_id": random.randint(1, 2_147_483_647),
    }
    if keyboard:
        payload_data["keyboard"] = keyboard
    try:
        api.messages.send(**payload_data)
    except ApiError as error:
        if keyboard and error.code == 911:
            payload_data.pop("keyboard", None)
            payload_data["message"] = f"{text}\n\nСсылка на игру: {settings.mini_app_url}"
            api.messages.send(**payload_data)
        else:
            raise
    print(f"Sent message to peer_id={peer_id}", flush=True)


def parse_command(message: dict[str, Any]) -> str:
    raw_payload = message.get("payload")
    if not raw_payload:
        return ""
    if isinstance(raw_payload, dict):
        return str(raw_payload.get("command", "")).strip()
    try:
        data = json.loads(raw_payload)
    except json.JSONDecodeError:
        return ""
    return str(data.get("command", "")).strip()


def user_name(api: Any, user_id: int | None) -> str:
    if not user_id:
        return ""
    try:
        users = api.users.get(user_ids=user_id)
    except ApiError:
        return ""
    if not users:
        return ""
    return str(users[0].get("first_name", "")).strip()


def greeting_text(name: str = "") -> str:
    hello = f"Здравствуйте, {name}!" if name else "Здравствуйте!"
    return (
        f"{hello}\n\n"
        "Предлагаем пройти игру «Вокруг света за 80 дней» и получить скидку от ООО Путешествие.\n"
        "Хотите сыграть?"
    )


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

    offer_keyboard = make_offer_keyboard()
    start_keyboard = make_start_keyboard()
    empty_keyboard = make_empty_keyboard()

    print("VK bot started", flush=True)
    for event in longpoll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        message = event.object.message
        text = message.get("text", "").strip().lower()
        command = parse_command(message)
        peer_id = message["peer_id"]
        print(f"Got message peer_id={peer_id} text={text!r} command={command!r}", flush=True)

        if command == "play_yes" or text in YES_WORDS:
            send_message(
                api,
                peer_id,
                "Отлично! Нажмите кнопку «Начать», чтобы открыть карту мира и выбрать уровень сложности.",
                start_keyboard,
            )
            continue

        if command == "play_no" or text in NO_WORDS:
            send_message(api, peer_id, "Хорошо, мы ждём вас снова!", empty_keyboard)
            continue

        if command in START_COMMANDS or text in START_WORDS or not text:
            name = user_name(api, message.get("from_id"))
            send_message(api, peer_id, greeting_text(name), offer_keyboard)
            continue

        send_message(api, peer_id, "Чтобы получить скидку, попробуйте пройти игру. Хотите сыграть?", offer_keyboard)


if __name__ == "__main__":
    main()
