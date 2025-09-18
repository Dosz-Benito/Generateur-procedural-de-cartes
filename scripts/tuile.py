"""Module définissant la classe Tuile pour représenter les éléments de la carte."""

from __future__ import annotations
from typing import Any, Sequence
import pygame
from scripts.type import TypeTuile, TypeDecoration

TAILLE_TUILE = 16


def pos_en_str(pos: Sequence[int]) -> str:
    """Convertit une position (x, y) en chaîne de caractères."""
    return f"{int(pos[0])};{int(pos[1])}"


class Decoration(pygame.sprite.Sprite):
    """Représente un élément décoratif dans la carte du jeu.

    Cette classe de base gère l'affichage, la sérialisation et les propriétés
    communes des éléments décoratifs avec position flottante, type et apparence.
    Elle est conçue pour être héritée par des classes spécifiques comme Tuile.
    """

    def __init__(self, type: TypeDecoration, index: int, pos: tuple[float, float], image: pygame.Surface, taille: int = TAILLE_TUILE) -> None:
        """Initialise un nouvel élément décoratif.

        Args:
            type (TypeDecoration): Type de l'élément décoratif
            index (int): Index de l'image dans la liste des images
            pos (tuple[float, float]): Position (x, y) flottante dans la carte
            image (pygame.Surface): Surface Pygame de l'image de l'élément
            taille (int, optional): Taille de l'élément en pixels. Défaut à TAILLE_TUILE.
        """
        super().__init__()
        self.type: TypeDecoration = type
        self.index: int = index
        self.pos: tuple[float, float] = pos
        self.taille: int = taille
        self._image: pygame.Surface = image.copy()

    @property
    def image(self) -> pygame.Surface:
        """Retourne la surface image actuelle de l'élément décoratif."""
        return self._image

    @image.setter
    def image(self, nouvelle_image: pygame.Surface) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Modifie la surface image de l'élément décoratif.

        Args:
            nouvelle_image (pygame.Surface): Nouvelle surface Pygame à utiliser
        """
        self._image = nouvelle_image.copy()

    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None:
        """Affiche l'élément décoratif sur la surface donnée avec un décalage.

        Args:
            surface (pygame.Surface): Surface Pygame où afficher l'élément
            decalage (pygame.Vector2): Décalage de la caméra (x, y)
        """
        surface.blit(
            self.image,
            (self.pos[0] * self.taille - decalage[0], self.pos[1] * self.taille - decalage[1])
        )

    def en_dict(self) -> dict[str, Any]:
        """Convertit l'élément décoratif en dictionnaire pour la sérialisation.

        Returns:
            Dictionnaire contenant les informations de l'élément décoratif
        """
        return {
            "type": self.type,
            "index": self.index,
            "pos": self.pos
        }

    @classmethod
    def de_dict(cls, infos: dict, image: pygame.Surface) -> Decoration:
        """Crée un élément décoratif à partir d'un dictionnaire.

        Args:
            infos (dict): Dictionnaire contenant les informations de l'élément
            image (pygame.Surface): Surface Pygame de l'image de l'élément

        Returns:
            Decoration: Nouvelle instance de Decoration
        """
        return cls(infos["type"], infos["index"], tuple(infos["pos"]), image)

    def __repr__(self) -> str:
        """Représentation string de l'élément décoratif pour le débogage."""
        return f"Decoration(type={self.type}, index={self.index}, pos={self.pos})"


class Tuile(Decoration):
    """Représente une tuile individuelle dans la carte du jeu.

    Cette classe hérite de Decoration et spécialise le comportement pour les tuiles
    en utilisant des positions entières et un type spécifique de tuile.
    """

    def __init__(self, type: TypeTuile, pos: tuple[int, int], index: int, image: pygame.Surface) -> None:
        """Initialise une nouvelle tuile.

        Args:
            type (TypeTuile): Type de la tuile (herbe ou pierre)
            pos (tuple[int, int]): Position (x, y) entière dans la grille
            index (int): Index de l'image dans la liste des images
            image (pygame.Surface): Surface Pygame de l'image de la tuile
        """
        super().__init__(type, index, pos, image) # pyright: ignore[reportArgumentType]
        self.pos: tuple[int, int] # pyright: ignore[reportIncompatibleVariableOverride]
        self.type: TypeTuile # pyright: ignore[reportIncompatibleVariableOverride]

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
        return f"Tuile(type={self.type}, pos={(int(self.pos[0]), int(self.pos[1]))}, index={self.index})"