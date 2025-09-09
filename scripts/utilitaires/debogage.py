"""Module utilitaire pour l'affichage de messages de débogage à l'écran."""

from typing import Any, Optional
import pygame

TAILLE_POLICE_DEFAUT = 30

pygame.font.init()
police_debogage = pygame.font.Font(None, TAILLE_POLICE_DEFAUT)
surface_ecran: pygame.Surface = pygame.display.get_surface()


def afficher_debug(
    information: str | int | float,
    *,
    x: int = 0,
    y: int = 0,
    couleur: pygame.Color = pygame.Color("white"),
    antialias: bool = False,
    wraplength: Optional[int] = 0,
    alignement: int = pygame.FONT_LEFT
) -> None:
    """Affiche un message de débogage à l'écran.

    Args:
        information (str | int | float): Information à afficher (sera convertie en string)
        x (int): Position X du texte
        y (int): Position Y du texte
        couleur (pygame.Color): Couleur du texte
        antialias (bool): Active l'anti-crénelage
        wraplength (Optional[int]): Largeur maximale du texte (0 = largeur de l'écran)
        alignement (int): Alignement du texte (pygame.FONT_LEFT, CENTER, RIGHT)
    """
    surface_ecran = pygame.display.get_surface()
    police_debogage.align = alignement
    surface_texte: pygame.Surface = police_debogage.render(
        str(information),
        antialias,
        couleur,
        wraplength=wraplength if wraplength else surface_ecran.get_width()
    )
    surface_ecran.blit(surface_texte, (x, y))


def afficher_image_debug(image: pygame.Surface, x: int = 0, y: int = 0) -> None:
    """Affiche une image de débogage à l'écran.

    Args:
        image (pygame.Surface): Surface Pygame à afficher
        x (int): Position X de l'image
        y (int): Position Y de l'image
    """
    surface_ecran = pygame.display.get_surface()
    surface_ecran.blit(image, (x, y))
