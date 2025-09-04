from __future__ import annotations
from typing import Literal, Sequence
import pygame
from scripts.parametres import INDEXS_DE_DECALAGES


def pos_en_str(pos: Sequence[int]) -> str:
    return f"{int(pos[0])};{int(pos[1])}"

class Tuile:
    def __init__(self, type: Literal["herbe"], pos: tuple[int, int] | list[int, int], index: int, images: list[pygame.Surface]) -> None: # pyright: ignore[reportInvalidTypeArguments]
        self.type = type
        self.pos: list[int] = list(pos)
        self.index = index
        self.taille: int = 16
        self.images: list[pygame.Surface] = [image.copy() for image in images] #! Il ne doit pas y avoir de copy()

    @property
    def loc(self):
        return f"{self.pos[0]};{self.pos[1]}"   

    def tuiles_autour(self, carte):
        tuiles: list[Tuile] = []
        for (dec_x, dec_y) in INDEXS_DE_DECALAGES:
            pos = self.pos[0] + dec_x, self.pos[1] + dec_y
            if carte.tuile_presente(pos):
                tuiles.append(self)
        return tuiles

    
    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2):
        surface.blit(self.images[self.index], (self.pos[0] * self.taille-decalage[0], self.pos[1] * self.taille-decalage[1]))
    
    def __repr__(self) -> str:
        return f"Tuile({self.type=}, {self.pos=}, {self.index=})"