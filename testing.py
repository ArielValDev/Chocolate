from amulet_nbt import StringTag
from models.buffer import Buffer

test1 = Buffer()
test2 = Buffer()

def add_text_component(buf: Buffer, text: str):
        text_bytes = text.encode()
        buf.bytearray_.append(8) # Meaning string tag
        buf.bytearray_.extend(len(text_bytes).to_bytes(2))
        buf.bytearray_.extend(text_bytes)
