import requests
from uuid import UUID

from models.buffer import OptionalString

def fetch_player_properties(uuid: UUID) -> list[tuple[str, str, OptionalString]]:
    data = requests.get(
        f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    ).json()

    if "properties" not in data:
        raise Exception("Player profile has no properties")

    properties: list[dict[str, str]] = data["properties"]

    to_return: list[tuple[str, str, OptionalString]] = []
    for prop in properties:
        to_return.append((prop["name"], prop["value"], OptionalString(prop.get("signature", None))))

    return to_return
