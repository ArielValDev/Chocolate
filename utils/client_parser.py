import zipfile
from constants import constants
import json


def _is_in_registry(registry: str):
    with open(constants.REGISTRIES_FILE, "r") as file:
        regs = json.load(file) 
        return f"minecraft:{registry}" in regs

def expand_tags(tags: dict[str, dict[str, list[str]]]) -> dict[str, dict[str, list[str]]]:
    changed = False
    for reg in tags:
        for tag_name in tags[reg]:
            for i, val in enumerate(tags[reg][tag_name]):
                if not val.startswith('#'): continue
                tags[reg][tag_name].pop(i)
                tags[reg][tag_name].extend(tags[reg][val[11:]]) # #minecraft:
                changed = True
    if changed:
        return expand_tags(tags)
    return tags

def get_named_tags():
    tags: dict[str, dict[str, list[str]]] = {}
    with zipfile.ZipFile("client.jar", "r") as jar:
        tag_files = filter(lambda n: n.startswith("data/minecraft/tags/"), jar.namelist())
        for raw_file in tag_files:
            file = raw_file.removeprefix("data/minecraft/tags/")
            registry = file.split('/')[0]
            #filter to only registries
            if not _is_in_registry(registry): 
                continue

            parts = file.split('/')
            registry_name = parts[0]
            tag_name = parts[-1].removesuffix(".json")

            values: list[str] = []
            with jar.open(raw_file) as file:
                values = json.load(file)["values"]
            
            if registry_name not in tags: tags[registry_name] = {}
            tags[registry_name][tag_name] = values
    
    return expand_tags(tags)
            


def get_tags_into_file():
    named_tags = get_named_tags()
    with open(constants.REGISTRIES_FILE, 'r') as file:
        registries = json.load(file)
    
    for reg in named_tags:
        entries = registries[f"minecraft:{reg}"]
        for tag in named_tags[reg]:
            new_values = list(map(lambda e: entries.index(e), named_tags[reg][tag]))
            named_tags[reg][tag] = new_values
    
    with open(constants.TAGS_FILE, "w") as file:
        json.dump(named_tags, file)