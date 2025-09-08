from __future__ import annotations
from typing import Any, Literal, Sequence
import pygame

from scripts.type import TypeTuile


def pos_en_str(pos: Sequence[int]) -> str:
    return f"{int(pos[0])};{int(pos[1])}"

class Tuile:
    def __init__(self, type: TypeTuile, pos: tuple[int, int], index: int, images: list[pygame.Surface]) -> None: # pyright: ignore[reportInvalidTypeArguments]
        self.type: TypeTuile = type
        self.pos: tuple[int, int] = pos
        self.index: int = index
        self.taille: int = 16
        self.images: list[pygame.Surface] = images

    @property
    def loc(self) -> str:
        return f"{self.pos[0]};{self.pos[1]}"
    
    @property
    def image(self) -> pygame.Surface:
        return self.images[self.index]

    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None:
        surface.blit(self.image, (self.pos[0] * self.taille-decalage[0], self.pos[1] * self.taille-decalage[1]))

    def en_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "pos": self.pos,
            "index": self.index
        }

    @classmethod
    def from_dict(cls, data: dict, images: list[pygame.Surface]) -> Tuile:
        return cls(data["type"], tuple(data["pos"]), data["index"], images)

    def __repr__(self) -> str:
        return f"Tuile({self.type=}, {self.pos=}, {self.index=})"