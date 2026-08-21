"""Module définissant la classe Tuile pour représenter les éléments de la carte."""
# dans tuile.py, ajoute une classe héritant de pygame.sprite.Sprite et héritée de Tuile et Decoration. Elle contient tous les attributs et fonctions qui seront communs à Tuile et Decoration (rect, image, en_dict, .... avec les types appropriés)
from __future__ import annotations
from typing import Any, Sequence
import pygame
from .parametres.type import TypeElement, TypeEntite, TypeTuile, TypeDecoration


def pos_en_str(pos: Sequence[int | float]) -> str:
    """Convertit une position (x, y) en chaîne de caractères."""
    return f"{int(pos[0])};{int(pos[1])}"

class ElementSprite(pygame.sprite.Sprite):
    """Classe de base pour les éléments sprite comme Tuile et Decoration.

    Cette classe contient les attributs et méthodes communs à tous les éléments
    sprite du jeu, tels que la position, l'image, le rectangle, etc.
    """

    def __init__(self, type: TypeElement, index: int, pos: tuple[float, float], image: pygame.Surface) -> None:
        """Initialise un nouvel élément sprite.

        Args:
            type (TypeElement): Type de l'élément
            index (int): Index de l'image
            pos (tuple[float, float]): Position (x, y) flottante absolue (en pixels)
            image (pygame.Surface): Surface Pygame de l'image
        """
        super().__init__()
        self.type: TypeElement = type
        self.index: int = index

        self.rect: pygame.Rect = image.get_rect(topleft=pos)
        self.image: pygame.Surface = image

    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None:
        """Affiche l'élément sur la surface donnée avec un décalage.

        Args:
            surface (pygame.Surface): Surface où afficher
            decalage (pygame.Vector2): Décalage de la caméra
        """
        surface.blit(
            self.image,
            (self.rect.x - decalage[0], self.rect.y - decalage[1])
        )

    def en_dict(self) -> dict[str, Any]:
        """Convertit l'élément en dictionnaire pour la sérialisation.

        Returns:
            dict: Dictionnaire avec les informations de l'élément
        """
        return {
            "type": self.type,
            "index": self.index,
            "pos": (self.rect.x, self.rect.y)
        }

    @classmethod
    def de_dict(cls, infos: dict[str, Any], image: pygame.Surface) -> ElementSprite:
        """Crée un élément décoratif à partir d'un dictionnaire.

        Args:
            infos (dict[str, Any]): Dictionnaire contenant les informations de l'élément
            image (pygame.Surface): Surface Pygame de l'image de l'élément

        Returns:
            Decoration: Nouvelle instance de Decoration
        """
        instance = cls(infos["type"], infos["index"], infos["pos"], image)
        return instance

    def __repr__(self) -> str:
        """Représentation string de l'élément pour le débogage."""
        return f"ElementSprite(type={self.type}, index={self.index}, pos={self.rect.topleft})"

class Decoration(ElementSprite):
    """Représente un élément décoratif dans la carte du jeu.

    Cette classe de base gère l'affichage, la sérialisation et les propriétés
    communes des éléments décoratifs avec position flottante, type et apparence.
    Elle est conçue pour être héritée par des classes spécifiques comme Tuile.
    """

    def __init__(self, type: TypeDecoration, index: int, pos: tuple[float, float], image: pygame.Surface) -> None:
        """Initialise un nouvel élément décoratif.

        Args:
            type (TypeDecoration): Type de l'élément décoratif
            index (int): Index de l'image dans la liste des images
            pos (tuple[float, float]): Position (x, y) flottante dans la carte
            image (pygame.Surface): Surface Pygame de l'image de l'élément
        """
        super().__init__(type, index, pos, image)
        self.type: TypeDecoration # pyright: ignore[reportIncompatibleVariableOverride]

class Tuile(ElementSprite):
    """Représente une tuile individuelle dans la carte du jeu.

    Cette classe hérite de Decoration et spécialise le comportement pour les tuiles
    en utilisant des positions entières et un type spécifique de tuile.
    """

    def __init__(self, type: TypeTuile, index: int, pos: tuple[float, float], image: pygame.Surface) -> None:
        """Initialise une nouvelle tuile.

        Args:
            type (TypeTuile): Type de la tuile (herbe ou pierre)
            pos (tuple[float, float]): Position (x, y) absolue en pixels
            index (int): Index de l'image dans la liste des images
            image (pygame.Surface): Surface Pygame de l'image de la tuile
        """
        super().__init__(type, index, pos, image)

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
        instance = cls(infos["type"], infos["index"], infos["pos"], image)
        return instance

    def __repr__(self) -> str:
        """Représentation string de la tuile pour le débogage."""
        return f"Tuile(type={self.type}, pos={self.rect.topleft}, index={self.index})"

class Entite(ElementSprite):
    def __init__(self, type: TypeEntite, pos: tuple[float, float], image: pygame.Surface) -> None:
        super().__init__(type, 0, pos, image)

    @classmethod
    def de_dict(cls, infos: dict[str, Any], image: pygame.Surface) -> Entite:
        return cls(infos["type"], infos["pos"], image)
