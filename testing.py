from models.buffer import Buffer
from models.types.position import *

p = Position(8, 1, 8)
buf = Buffer()
buf.add_position(p)
print(p)
print(buf.get_bytes())
print(buf.consume_position())