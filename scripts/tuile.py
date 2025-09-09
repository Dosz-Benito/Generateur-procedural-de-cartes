"""Module définissant la classe Tuile pour représenter les éléments de la carte."""

from __future__ import annotations
from typing import Any, Sequence
import pygame
from scripts.type import TypeTuile

TAILLE_TUILE_DEFAUT = 16


def pos_en_str(pos: Sequence[int]) -> str:
    """Convertit une position (x, y) en chaîne de caractères."""
    return f"{int(pos[0])};{int(pos[1])}"


class Tuile(pygame.sprite.Sprite):
    """Représente une tuile individuelle dans la carte du jeu.

    Cette classe hérite de pygame.sprite.Sprite et gère l'affichage et
    la sérialisation d'une tuile avec son type, position et apparence.
    """

    def __init__(self, type: TypeTuile, pos: tuple[int, int], index: int, image: pygame.Surface) -> None:
        """Initialise une nouvelle tuile.

        Args:
            type (TypeTuile): Type de la tuile
            pos (tuple[int, int]): Position (x, y) dans la grille
            index (int): Index de l'image dans la liste des images
            image (pygame.Surface): Surface Pygame de l'image de la tuile
        """
        super().__init__()
        self.type: TypeTuile = type
        self.pos: tuple[int, int] = pos
        self.index: int = index
        self.taille: int = TAILLE_TUILE_DEFAUT
        self._surface_image: pygame.Surface = image.copy()

    @property
    def localisation(self) -> str:
        """Retourne la localisation de la tuile sous forme de chaîne."""
        return f"{self.pos[0]};{self.pos[1]}"

    @property
    def image(self) -> pygame.Surface:
        """Retourne la surface image actuelle de la tuile."""
        return self._surface_image

    @image.setter
    def image(self, nouvelle_image: pygame.Surface) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Modifie la surface image de la tuile.

        Args:
            nouvelle_image (pygame.Surface): Nouvelle surface Pygame à utiliser
        """
        self._surface_image = nouvelle_image.copy()

    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None:
        """Affiche la tuile sur la surface donnée avec un décalage.

        Args:
            surface (pygame.Surface): Surface Pygame où afficher la tuile
            decalage (pygame.Vector2): Décalage de la caméra (x, y)
        """
        surface.blit(
            self.image,
            (self.pos[0] * self.taille - decalage[0], self.pos[1] * self.taille - decalage[1])
        )

    def en_dict(self) -> dict[str, Any]:
        """Convertit la tuile en dictionnaire pour la sérialisation.

        Returns:
            Dictionnaire contenant les informations de la tuile
        """
        return {
            "type": self.type,
            "pos": self.pos,
            "index": self.index
        }

    @classmethod
    def de_dict(cls, infos: dict, image: pygame.Surface) -> Tuile:
        """Crée une tuile à partir d'un dictionnaire.

        Args:
            infos (dict): Dictionnaire contenant les informations de la tuile
            image (pygame.Surface): Surface Pygame de l'image de la tuile

        Returns:
            Tuile: Nouvelle instance de Tuile
        """
        return Tuile(infos["type"], tuple(infos["pos"]), infos["index"], image)

    def __repr__(self) -> str:
        """Représentation string de la tuile pour le débogage."""
        return f"Tuile({self.type=}, {self.pos=}, {self.index=})"