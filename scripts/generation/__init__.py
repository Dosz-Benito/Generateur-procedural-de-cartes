from typing import Literal
import pygame
from scripts.carte import Carte
from scripts.generation.generateur_carte import GenerateurCarte
from scripts.parametres import NOMBRE_TUILES
from scripts.parametres.type import TypeDecoration, TypeEntite, TypeTuile


generateur_terrain: GenerateurCarte = GenerateurCarte(NOMBRE_TUILES)

def generer_carte(type_terrain: Literal["Ile", "Bloc"], images_tuiles: dict[TypeTuile, list[pygame.Surface]], images_deco: dict[TypeDecoration, list[pygame.Surface]], images_entites: dict[TypeEntite, pygame.Surface]) -> Carte:
    """Génère une nouvelle carte complète, avec les tuiles, la décoration, le joueur et les ennemis.

    Args:
        type_terrain (Literal[&quot;Ile&quot;, &quot;Bloc&quot;]): Le type de terrain à utiliser pour la génération.
    """
    carte = generateur_terrain.generer(type_terrain, images_tuiles, images_deco, images_entites)
    return carte