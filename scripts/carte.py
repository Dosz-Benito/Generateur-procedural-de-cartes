# grass: herbe
# stone: pierre
# neighbor offset: décalage du voisin
# offset: compenser
from typing import Any
import pygame
from scripts.parametres import INDEXS_DE_DECALAGES
from scripts.utilitaires import Tuile, loc_en_tuple

# * Constantes
TYPES_OBSTACLES: list[str] = ['herbe', 'pierre']
TYPES_AUTOTUILES = {"herbe", "pierre"}
CARTE_AUTOTUILES: dict[tuple[tuple[int, int], ...], int]= {
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
    tuple(sorted([(1, 0)])): 0,
}

class Carte:
    """Une classe représentant une carte"""

    def __init__(self, jeu:Any, taille: int = 16) -> None:
        self.jeu: Any = jeu
        self.taille_tuile: int = taille
        self.carte: dict[str, Tuile] = {}
        self.carte_deco = {}

    def tuile_presente(self, pos: tuple[int, int]) -> bool:
        return True if self.carte.get(f"{pos[0]};{pos[1]}") else False

    def redessiner(self):
        """Redéssine la carte"""
        for index_, tuile in self.carte.items():
            decalages_alentour = set()
            for dec in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                loc = str(tuile['pos'][0] + dec[0]) + ';' + str(tuile['pos'][1] + dec[1])
                if loc in self.carte:
                    # if tuile['type'] == self.carte[loc]['type']:
                        decalages_alentour.add(dec)
            decalages_alentour = tuple(sorted(decalages_alentour))
            if (tuile['type'] in TYPES_AUTOTUILES) and (decalages_alentour in CARTE_AUTOTUILES):
                tuile['index'] = CARTE_AUTOTUILES[decalages_alentour]

    def afficher(self, surface: pygame.Surface, decalage:list[float]) -> None:
        for tuile in self.carte.values():
            surface.blit(self.jeu.rsc[tuile["type"]][tuile["index"]], (tuile["pos"][0] * self.taille_tuile-decalage[0], tuile["pos"][1] * self.taille_tuile-decalage[1]))
