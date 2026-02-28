import json
import requests
from uuid import UUID
from constants import constants
import zipfile

from models.buffer import OptionalString

def fetch_player_properties(uuid: UUID) -> list[tuple[str, str, OptionalString]]:
    data = requests.get(
        f"{constants.MOJANG_PROFILE_API}{uuid}"
    ).json()

    if "properties" not in data:
        raise Exception("Player profile has no properties")

    properties: list[dict[str, str]] = data["properties"]

    to_return: list[tuple[str, str, OptionalString]] = []
    for prop in properties:
        to_return.append((prop["name"], prop["value"], OptionalString(prop.get("signature", None))))

    return to_return

def get_registries_from_file(url: str) -> dict[str, list[str]]:
    to_return: dict[str, list[str]] = {}

    with open(constants.REGISTRIES_FILE, "r") as file:
        registries: dict[str, list[str]] = json.load(file)
    for reg, data in registries.items():
        to_return[reg] = data
    
    return to_return

def fetch_version_client():
    versions = requests.get(constants.VERSION_MANIFEST).json()
    version_url = ""
    for version in versions["versions"]:
        if version["id"] == constants.VERSION:
            version_url = version["url"]
            break
    if version_url == "":
        raise Exception("Didn't find version url")
    
    version = requests.get(version_url).json()
    client_jar_url = version["downloads"]["client"]["url"]
    client_jar_response = requests.get(client_jar_url)

    client_jar_response = requests.get(client_jar_url)
    client_jar_response.raise_for_status()

    with open("client.jar", "wb") as f:
        f.write(client_jar_response.content)

def fetch_registries_into_file():
    registries: dict[str, list[str]] = {}
    with zipfile.ZipFile("client.jar", "r") as jar:
        for file in jar.namelist():
            if not file.startswith("data/minecraft/"):
                continue
            if not file.endswith(".json"):
                continue

            if "enchantment/" in file or "flie/" in file: continue

            relative_path = file.replace("data/minecraft/", "")   

            parts = relative_path.split("/")
            if len(parts) < 2:
                continue
            
            registry_name = parts[0]
            if parts[0] == "worldgen":
                if parts[1] != "biome": continue
                registry_name = parts[0] + '/' + parts[1]
            file_name = parts[-1].replace(".json", "")
            
            registry_key = f"minecraft:{registry_name}"
            entry_key = f"minecraft:{file_name}"
            
            if registry_key not in registries:
                registries[registry_key] = []

            registries[registry_key].append(entry_key)

    with open("constants/registry_data.json", "w", encoding="utf-8") as f:
        json.dump(registries, f)

