from typing import Any, Sequence
import pygame
from scripts.tuile import Tuile, pos_en_str
from scripts.parametres import INDEXS_DE_DECALAGES_DIAGONAUX, INDEXS_DE_DECALAGES_DROITS
from scripts.utilitaires import maths

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
    tuple(sorted([(0, -1)])): 5,
    tuple(sorted([(1, 0)])): 0,
}

class Carte:
    """Une classe représentant une carte"""

    def __init__(self, jeu:Any, taille: int = 16) -> None:
        self.jeu: Any = jeu
        self.taille_tuile: int = taille
        self.carte: dict[str, Tuile] = {}

    def tuile_presente(self, pos: Sequence[int]) -> bool:
        return True if self.carte.get(pos_en_str(pos)) else False # pyright: ignore[reportArgumentType]

    def ajouter_tuile(self, x: int, y: int) -> None:
        self.carte[f"{int(x)};{int(y)}"] = Tuile("herbe", (x, y), 0, self.jeu.rsc["herbe"])

    def enlever_tuile(self, x: int, y: int) -> None:
        del self.carte[f"{x};{y}"]

    def entourer(self, tuile: Tuile):
        tuiles_autour_droit: list[Tuile] = [] # Liste des tuiles autour de nous en droit
        for dec_x, dec_y in INDEXS_DE_DECALAGES_DROITS:
            pos = tuile.pos[0] + dec_x, tuile.pos[1] + dec_y
            if self.tuile_presente(pos):
                loc = pos_en_str(pos)
                tuiles_autour_droit.append(self.carte[loc])
        nb_tuiles_autour_droit: int = len(tuiles_autour_droit)

        tuiles_autour_diagonales: list[Tuile] = [] # Liste des tuiles autour de nous en diagonale
        for dec_x, dec_y in INDEXS_DE_DECALAGES_DIAGONAUX:
            pos = tuile.pos[0] + dec_x, tuile.pos[1] + dec_y
            if self.tuile_presente(pos):
                loc = pos_en_str(pos)
                tuiles_autour_diagonales.append(self.carte[loc])
        nb_tuiles_autour_diagonales: int = len(tuiles_autour_diagonales)

        match nb_tuiles_autour_droit:
            case 0:
                match nb_tuiles_autour_diagonales:
                    case 0:
                        print(f"Une tuile {self} est au milieu de nulle part !!!")
                        raise
                    case 1:
                        self.enlever_tuile(*tuiles_autour_diagonales[0].pos)
                    case 2:
                        tuile.pos[1] += 1
                        self.ajouter_profondeur(tuile)
                        for t in [*tuiles_autour_diagonales]:
                            self.ajouter_profondeur(t)
                    case 3:
                        # Quand il y a 3 tuiles autour, on comble les 2 espaces vides
                        pos_x: set[int] = set()
                        pos_y: set[int] = set()
                        for voisine in tuiles_autour_diagonales:
                            pos_x.add(voisine.pos[0])
                            pos_y.add(voisine.pos[1])
                        # pos_x contient 2 positions en x : celles des tuiles à notre gauche et à notre droite
                        for x in pos_x:
                            self.ajouter_tuile(x, tuile.pos[1])
                        for y in pos_y:
                            self.ajouter_tuile(tuile.pos[0], y)
                    case 4:
                        for voisine in tuiles_autour_diagonales:
                            pos_voisine = voisine.pos
                            x = tuile.pos[0] - maths.signe(tuile.pos[0] - pos_voisine[0])
                            y = tuile.pos[1] - maths.signe(tuile.pos[1] - pos_voisine[1])
                            self.ajouter_tuile(x, tuile.pos[1])
                            self.ajouter_tuile(tuile.pos[0], y)
            case 1:
                match nb_tuiles_autour_diagonales:
                    case 1:
                        pass
                    case 2:
                        # if len(set([t.pos[1] for t in]))
                        for tuile in tuiles_autour_diagonales:
                            if tuile.pos[0] == tuiles_autour_droit[0].pos[0]:
                                self.ajouter_tuile(tuile.pos[0], tuile.pos[1] - (tuile.pos[1] - tuile.pos[1]))
                    case 3 | 4:
                        # Quand il y a 3 tuiles autour, on comble les 2 espaces vides
                        pos_x: set[int] = set()
                        pos_y: set[int] = set()
                        for voisine in tuiles_autour_diagonales:
                            pos_x.add(voisine.pos[0])
                            pos_y.add(voisine.pos[1])
                        # pos_x contient 2 positions en x : celles des tuiles à notre gauche et à notre droite
                        for x in pos_x:
                            self.ajouter_tuile(x, tuile.pos[1])
                        for y in pos_y:
                            self.ajouter_tuile(tuile.pos[0], y)

    def ajouter_profondeur(self, tuile: Tuile):
        for _ in range(1, 11): # 10-pos[1]
            self.ajouter_tuile(tuile.pos[0], tuile.pos[1]+_)


    def redessiner(self):
        """Redéssine la carte"""
        for _, tuile in self.carte.items():
            decalages_alentour = set()
            for dec in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                pos = tuile.pos[0] + dec[0], tuile.pos[1] + dec[1]
                if self.tuile_presente(pos):
                    # if tuile['type'] == self.carte[loc]['type']:
                        decalages_alentour.add(dec)
            decalages_alentour = tuple(sorted(decalages_alentour))
            if (tuile.type in TYPES_AUTOTUILES) and (decalages_alentour in CARTE_AUTOTUILES):
                tuile.index = CARTE_AUTOTUILES[decalages_alentour]
            else:
                print(f"[Carte.redessiner] Index adéquat introuvable pour la tuile {tuile}, {decalages_alentour=}")

    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None:
        for tuile in self.carte.values():
            tuile.afficher(surface, decalage)
