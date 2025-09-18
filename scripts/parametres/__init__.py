"""Paramètres et constantes globales du projet de génération procédurale de cartes."""

import pygame
from scripts.type import TypeDecoration, TypeTuile

#* Jeu en général
TAILLE_ECRAN: tuple[float, float] = (1690, 800)
TAILLE_AFFICHAGE: tuple[float, float] = (TAILLE_ECRAN[0] * 0.98, TAILLE_ECRAN[1] * 0.98)
FPS: int = 60
VITESSE_CAMERA: int = 10
NOMBRE_TUILES = 500

#* --------- Commandes de navigation ---------
DECALER_GAUCHE: int = pygame.K_LEFT
DECALER_DROITE: int = pygame.K_RIGHT
DECALER_HAUT: int = pygame.K_UP
DECALER_BAS: int = pygame.K_DOWN
GENERER_CARTE_ILES: int = pygame.K_i
GENERER_CARTE: int = pygame.K_p


#* --------- Génération procédurale ---------
# Décalages directionnels
DECALAGE_HAUT_GAUCHE: tuple[int, int] = (-1, -1)
DECALAGE_HAUT: tuple[int, int] = (0, -1)
DECALAGE_HAUT_DROITE: tuple[int, int] = (1, -1)
DECALAGE_GAUCHE: tuple[int, int] = (-1, 0)
DECALAGE_DROITE: tuple[int, int] = (1, 0)
DECALAGE_BAS_GAUCHE: tuple[int, int] = (-1, 1)
DECALAGE_BAS: tuple[int, int] = (0, 1)
DECALAGE_BAS_DROITE: tuple[int, int] = (1, 1)
INDEXS_DECALAGES: list[tuple[int, int]] = [
    DECALAGE_HAUT_GAUCHE, DECALAGE_HAUT, DECALAGE_HAUT_DROITE,
    DECALAGE_GAUCHE, DECALAGE_DROITE, DECALAGE_BAS_GAUCHE,
    DECALAGE_BAS, DECALAGE_BAS_DROITE
]
INDEXS_DECALAGES_DIAGONAUX: list[tuple[int, int]] = [
    DECALAGE_HAUT_GAUCHE, DECALAGE_HAUT_DROITE,
    DECALAGE_BAS_GAUCHE, DECALAGE_BAS_DROITE
]
INDEXS_DECALAGES_DROITS: list[tuple[int, int]] = [
    DECALAGE_HAUT, DECALAGE_BAS, DECALAGE_GAUCHE, DECALAGE_DROITE
]

# Constantes pour le redessinage
TYPES_TUILES: list[TypeTuile] = ['herbe', 'pierre']
TYPES_DECORATION: list[TypeDecoration] = ["arbre", "plante"]
TYPES_REDESSIN: list[TypeTuile] = ["herbe", "pierre"]
CARTE_REDESSIN: dict[tuple[tuple[int, int], ...], int]= {
    tuple(sorted([(0 ,1), (1, 0)])): 0, # *En haut à gauche
    tuple(sorted([(-1, 0), (1, 0), (0, 1)])): 1, # *En haut au centre
    tuple(sorted([(-1, 0), (0, 1)])): 2, # *En haut à droite
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3, # *A droite
    tuple(sorted([(-1, 0), (0, -1)])): 4,# *En bas à droite
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,# *En bas au centre
    tuple(sorted([(0, -1), (1, 0)])): 6,# *En bas à gauche
    tuple(sorted([(0, -1), (0, 1), (1, 0)])): 7, # *A gauche
    tuple(sorted([(-1, 0), (0, -1), (1, 0), (0, 1)])): 8,# *Au milieu
    # ? Autres
    tuple(sorted([(1, 0)])): 0,
    tuple(sorted([(-1, 0), (1, 0)])): 1,
    tuple(sorted([(0, 1)])): 1,
    tuple(sorted([(1, 0)])): 1,
    tuple(sorted([(0, 1), (0, -1)])): 8,
    tuple(sorted([(-1, 0)])): 2,
    tuple(sorted([(0, -1)])): 5,
    tuple(sorted([(1, 0)])): 0,
}
