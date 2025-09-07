import pygame
AGRANDISSEMENT: float = 2.0
TAILLE_AFFICHAGE: tuple[int, int] = (900, 430)
TAILLE_ECRAN: tuple[float, float] = (TAILLE_AFFICHAGE[0] * AGRANDISSEMENT, TAILLE_AFFICHAGE[1]*AGRANDISSEMENT)

# Commandes
DECALER_GAUCHE: int = pygame.K_LEFT
DECALER_DROITE: int = pygame.K_RIGHT
DECALER_HAUT: int = pygame.K_UP
DECALER_BAS: int = pygame.K_DOWN
GENERER_CARTE: int = pygame.K_p


# Génération procédurale
DEC_HAUT_GAUCHE: tuple[int, int] = (-1, -1)
DEC_HAUT: tuple[int, int] = (0, -1)
DEC_HAUT_DROITE: tuple[int, int] = (1, -1)
DEC_GAUCHE: tuple[int, int] = (-1, 0)
DEC_DROITE: tuple[int, int] = (1, 0)
DEC_BAS_GAUCHE: tuple[int, int] = (-1, 1)
DEC_BAS: tuple[int, int] = (0, 1)
DEC_BAS_DROITE: tuple[int, int] = (1, 1)
INDEXS_DE_DECALAGES: list[tuple[int, int]] = [DEC_HAUT_GAUCHE, DEC_HAUT, DEC_HAUT_DROITE, DEC_GAUCHE, DEC_DROITE, DEC_BAS_GAUCHE, DEC_BAS, DEC_BAS_DROITE]
INDEXS_DE_DECALAGES_DIAGONAUX: list[tuple[int, int]] = [DEC_HAUT_GAUCHE, DEC_HAUT_DROITE, DEC_BAS_GAUCHE, DEC_BAS_DROITE]
INDEXS_DE_DECALAGES_DROITS: list[tuple[int, int]] = [DEC_HAUT, DEC_BAS, DEC_GAUCHE, DEC_DROITE]