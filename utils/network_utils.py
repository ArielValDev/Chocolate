from typing import Any

import requests
from uuid import UUID
from constants import *

from constants.constants import MOJANG_PROFILE_API, REGISTRIES_URL
from models.buffer import OptionalString

def fetch_player_properties(uuid: UUID) -> list[tuple[str, str, OptionalString]]:
    data = requests.get(
        f"{MOJANG_PROFILE_API}{uuid}"
    ).json()

    if "properties" not in data:
        raise Exception("Player profile has no properties")

    properties: list[dict[str, str]] = data["properties"]

    to_return: list[tuple[str, str, OptionalString]] = []
    for prop in properties:
        to_return.append((prop["name"], prop["value"], OptionalString(prop.get("signature", None))))

    return to_return

def fetch_registries(url: str) -> dict[str, list[str]]:
    to_return: dict[str, list[str]] = {}

    registries: dict[str, dict[str, Any]] = requests.get(REGISTRIES_URL).json()
    for reg, data in registries.items():
        to_return[reg] = list(data.keys())
    
    return to_return

