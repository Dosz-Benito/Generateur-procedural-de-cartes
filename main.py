from typing import Any, NoReturn, Optional
import pygame
import random
from scripts.carte import Carte
from scripts.utilitaires import debogage, loc_en_tuple
from scripts.utilitaires.outils_images import charger_images
from scripts.parametres import *
# Tester avec stubtest.exe

class Editeur:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Editeur de niveau")

        # Pour l'éditeur
        self.affichage = pygame.Surface(TAILLE_AFFICHAGE)
        self.ecran = pygame.display.set_mode(TAILLE_ECRAN, pygame.SRCALPHA)
        self.touches: dict[int, bool] = {}
        self.rsc: dict[str, Any] = {
            'herbe': charger_images("rsc/herbe"),
        }
        self.horloge = pygame.time.Clock()
        self.liste_types_tuiles = list(self.rsc)
        self.decalage: list[float] = [0, 0]
        self.carte = Carte(self)
        self.shift: bool = False

        # Pour la disposition des tuiles
        self.mouvement_x: list[int] = [0, 0]
        self.mouvement_y: list[int] = [0, 0]
        self.type_tuile: str = "arbres"  # self.liste_types_tuiles[0]
        self.index_type_tuile: int = 0  # TODO Enlever
        self.index_tuile: int = 1
        self.mpos: list[float]
        self.index_tuile_souris: tuple[int, int]
        self.img_trans: pygame.Surface

        # Pour les fichiers
        self.nom_fichier: Optional[str] = None
        
        # Pour la prévisualisation
        self.img_previs = pygame.Surface(TAILLE_ECRAN, pygame.SRCALPHA)
        self.img_previs.fill("grey")
        self.img_previs.set_alpha(8)
        
        self.generation_procedurale()

    def generation_procedurale(self):
        x, y = 0, 0
        print(x, y)
        self.ajouter_tuile(x, y)
        for _ in range(1, 401):
            while self.carte.tuile_presente((x, y)):
                x+=random.choice(random.choice(INDEXS_DE_DECALAGES_DIAGONAUX))
                y+=random.choice(random.choice(INDEXS_DE_DECALAGES_DIAGONAUX))
            self.ajouter_tuile(x, y)
        self.remplir()
        self.carte.redessiner()

    def remplir(self):
        for loc in self.carte.carte.copy().keys():
            autour: list[tuple[int, int]] = []
            loc_t = loc_en_tuple(loc)
            for dec_x, dec_y in INDEXS_DE_DECALAGES_DROITS:
                nouv_loc = (loc_t[0] + dec_x, loc_t[1] + dec_y)
                if self.carte.tuile_presente(nouv_loc):
                    autour.append(nouv_loc)
            if not autour:
                for x, y in INDEXS_DE_DECALAGES_DROITS:
                    self.ajouter_tuile(loc_t[0] + x, loc_t[1] + y)

    def ajouter_tuile(self, x, y):
        self.carte.carte[f"{x};{y}"] = {'type': 'herbe', 'pos': [x, y], 'index': 0}

    def lancer(self) -> NoReturn:
        while True:
            self.affichage.fill((0, 0, 0))
            self.appliquer_decalage()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == GENERER_CARTE:
                        self.tout_effacer()
                        self.generation_procedurale()
                    if event.key == DECALER_GAUCHE:
                        self.mouvement_x[0] = True
                    if event.key == DECALER_DROITE:
                        self.mouvement_x[1] = True
                    if event.key == DECALER_HAUT:
                        self.mouvement_y[0] = True
                    if event.key == DECALER_BAS:
                        self.mouvement_y[1] += True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == DECALER_GAUCHE:
                        self.mouvement_x[0] = False
                    if event.key == DECALER_DROITE:
                        self.mouvement_x[1] = False
                    if event.key == DECALER_HAUT:
                        self.mouvement_y[0] = False
                    if event.key == DECALER_BAS:
                        self.mouvement_y[1] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            self.carte.afficher(self.affichage, self.decalage)
            self.ecran.blit(pygame.transform.scale(self.affichage, TAILLE_ECRAN), (0, 0))
            self.ecran.blit(self.img_previs, self.img_previs.get_rect(center = (TAILLE_ECRAN[0] / 2, TAILLE_ECRAN[1] / 2)))
            debogage.deboguer(f"{self.nom_fichier if self.nom_fichier else "Nouvelle carte"}", couleur='yellow', alignement=pygame.FONT_CENTER)
            debogage.deboguer(self.decalage, couleur="yellow")
            pygame.display.update()
            self.horloge.tick(60)

    def appliquer_decalage(self):
        self.decalage[0] += (self.mouvement_x[1] - self.mouvement_x[0]) * 2
        self.decalage[1] += (self.mouvement_y[1] - self.mouvement_y[0]) * 2

    def tout_effacer(self):
        self.carte.carte_deco = {}
        self.carte.carte = {}


Editeur().lancer()
