"""Module utilitaire pour la gestion des images et ressources graphiques."""

import os
import random
import pygame

# Constantes
DOSSIER_GENERAL = "rsc/"
DOSSIER_SAUVEGARDES = DOSSIER_GENERAL + "cartes/"
DOSSIER_IMAGES = DOSSIER_GENERAL + "images/"
TYPES_DECORATIONS = {"plantes", "arbres", "rocher"}


def charger_image(fichier: str, couleur_transparente: tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface:
    """Charge une image et définit sa couleur transparente.

    Args:
        fichier (str): Chemin vers le fichier image
        couleur_transparente (tuple[int, int, int]): Couleur à rendre transparente (noir par défaut)

    Returns:
        pygame.Surface: Surface Pygame avec transparence
    """
    image: pygame.Surface = pygame.image.load(fichier).convert_alpha()
    image.set_colorkey(couleur_transparente)
    return image


def charger_images(dossier: str, couleur_transparente: tuple[int, int, int] = (0, 0, 0)) -> list[pygame.Surface]:
    """Charge toutes les images PNG d'un dossier.

    Args:
        dossier (str): Chemin du dossier contenant les images
        couleur_transparente (tuple[int, int, int]): Couleur à rendre transparente (noir par défaut)

    Returns:
        list[pygame.Surface]: Liste des surfaces Pygame chargées, triées par nom de fichier
    """
    images: list[pygame.Surface] = []
    for fichier in sorted(os.listdir(dossier)):
        if fichier.endswith(".png"):
            images.append(charger_image(dossier + '/' + fichier, couleur_transparente))
    return images