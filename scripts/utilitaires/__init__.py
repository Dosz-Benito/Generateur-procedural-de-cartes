from typing import Any, Literal, TypeAlias


Tuile: TypeAlias = dict[Literal['type', 'pos', 'index'], Any]

def loc_en_tuple(loc: str):
    return tuple([int(i) for i in loc.split(";")])