from typing import Any, Sequence
import pygame
from scripts.tuile import Tuile, pos_en_str
from scripts.parametres import INDEXS_DE_DECALAGES, INDEXS_DE_DECALAGES_DIAGONAUX, INDEXS_DE_DECALAGES_DROITS
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

    def remplir(self) -> None:
        """Cette fonction mets des tuiles dans les espaces vides et fermés de la carte"""
        for tuile in self.carte.copy().values():
            self.entourer(tuile)

    def entourer(self, tuile: Tuile) -> None:
        """Remplit les vides autour d'une tuile existante."""
        # Récupère les tuiles autour en droit et en diagonale
        voisins_droits: list[Tuile] = self._tuiles_autour(tuile, INDEXS_DE_DECALAGES_DROITS)
        voisins_diag: list[Tuile] = self._tuiles_autour(tuile, INDEXS_DE_DECALAGES_DIAGONAUX)

        nb_droits: int = len(voisins_droits)
        nb_diag: int = len(voisins_diag)

        # Cas où la tuile est isolée
        if nb_droits == 0 and nb_diag == 0:
            print(f"Une tuile {tuile} est au milieu de nulle part !!!")
            return

        # Supprime les tuiles diagonales seules si pas de voisins droits
        if nb_droits == 0 and nb_diag == 1:
            self.enlever_tuile(*voisins_diag[0].pos)
            return

        # Pour les autres configurations, on comble les vides selon les voisins
        if nb_droits == 0 and nb_diag in (2, 3, 4):
            # Décalage vertical pour 2 tuiles ou ajout de tuiles pour 3-4 tuiles
            if nb_diag == 2:
                tuile.pos = (tuile.pos[0], tuile.pos[1] + 1)
                self.ajouter_profondeur(tuile)
                for t in voisins_diag:
                    self.ajouter_profondeur(t)
            else:
                self._combler_espaces_vides(tuile, voisins_diag)
            return

        # Cas avec un voisin droit : on comble les diagonales si nécessaire
        if nb_droits == 1 and nb_diag in (2, 3, 4):
            self._combler_espaces_vides(tuile, voisins_diag)

    def _tuiles_autour(self, tuile: Tuile, decalages: list[tuple[int, int]] = INDEXS_DE_DECALAGES) -> list[Tuile]:
        """Renvoie la liste des tuiles présentes autour de la tuile selon les décalages donnés."""
        voisins: list[Tuile] = []
        for dx, dy in decalages:
            pos: tuple[int, int] = tuile.pos[0] + dx, tuile.pos[1] + dy
            if self.tuile_presente(pos):
                voisins.append(self.carte[pos_en_str(pos)])
        return voisins

    def _combler_espaces_vides(self, tuile: Tuile, voisins: list[Tuile]) -> None:
        """Ajoute des tuiles pour combler les espaces vides autour d'une tuile donnée."""
        pos_x: set[int] = {v.pos[0] for v in voisins}
        pos_y: set[int] = {v.pos[1] for v in voisins}
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
                pass
                # print(f"[Carte.redessiner] Index adéquat introuvable pour la tuile {tuile}, {decalages_alentour=}")

    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None:
        for tuile in self.carte.values():
            tuile.afficher(surface, decalage)
