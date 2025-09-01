import os
import random
import pygame
# Constantes
DOSSIER_GENERAL = "rsc/"
DOSSIER_CARTES = DOSSIER_GENERAL+"cartes/"
DOSSIER_IMAGES = DOSSIER_GENERAL + "images/"
TYPES_DECO = {"plantes", "arbres", "rocher"}
# Fonctions

def charger_image(fichier: str, couleur: tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface:
    image: pygame.Surface = pygame.image.load(fichier).convert_alpha()
    image.set_colorkey(couleur)
    return image


def charger_images(dossier: str, couleur: tuple[int, int, int] = (0, 0, 0)) -> list[pygame.Surface]:
    """Charge toutes les images d'un dossier

    Args:
        dossier (str): Chemin du dossier excluant rsc/images
        couleur (tuple[int, int, int], optional): La couleur à convertir en transparence. Defaults to (0, 0, 0).

    Returns:
        list[pygame.Surface]: La liste des images trouvées
    """
    images: list[pygame.Surface] = []
    for fichier in sorted(os.listdir(dossier)):
        if fichier.endswith(".png"):
            images.append(charger_image(dossier + '/' + fichier, couleur))
    return images