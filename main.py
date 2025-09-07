from typing import Any, Callable, NoReturn, Self
import pygame
import random
from scripts.carte import Carte
from scripts.utilitaires import debogage
from scripts.utilitaires.outils_images import charger_images
from scripts.parametres import *
# Tester avec stubtest.exe


class Editeur:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Editeur de niveau")

        # Pour l'éditeur
        self.affichage = pygame.Surface(TAILLE_AFFICHAGE)
        self.ecran: pygame.Surface = pygame.display.set_mode(TAILLE_ECRAN, pygame.SRCALPHA)
        self.rsc: dict[str, Any] = {
            'herbe': charger_images("rsc/herbe"),
        }
        self.horloge = pygame.time.Clock()
        self.decalage: pygame.Vector2 = pygame.Vector2()
        self.carte = Carte(self)

        # Pour la disposition des tuiles
        self.mouvement_x: list[int] = [0, 0]
        self.mouvement_y: list[int] = [0, 0]

        # Pour la génération procédurale
        self.nb_tuiles: int = 500
        self.p_haut: float = 0
        self.p_bas: float = 0
        self.p_gauche: float = 0
        self.p_droite: float = 0
        
        self.fonc_generation_procedurale()

    def generation_procedurale(self) -> None:
        x = n_x = 0
        y = n_y = 0
        self.p_haut, self.p_gauche = random.choice([(0.8, 0.8), (0.8, 0.2), (0.2, 0.8), (0.2, 0.2)])
        for _ in range(self.nb_tuiles):
            while self.carte.tuile_presente((n_x, n_y)):
                if random.random() < self.p_gauche:
                    n_x += DEC_GAUCHE[0]
                else:
                    n_x += DEC_DROITE[0]
                if random.random() < self.p_haut:
                    n_y += DEC_HAUT[1]
                else:
                    n_y += DEC_BAS[1]
            x: int = n_x
            y: int = n_y
            self.carte.ajouter_tuile(x, y)
        self.carte.redessiner()

    fonc_generation_procedurale: Callable[..., None] = generation_procedurale

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
                        self.decalage = pygame.Vector2()
                        self.tout_effacer()
                        self.fonc_generation_procedurale()
                    if event.key == DECALER_GAUCHE:
                        self.mouvement_x[0] = True
                    if event.key == DECALER_DROITE:
                        self.mouvement_x[1] = True
                    if event.key == DECALER_HAUT:
                        self.mouvement_y[0] = True
                    if event.key == DECALER_BAS:
                        self.mouvement_y[1] = True
                    if event.key == pygame.K_o:
                        self.carte.remplir()
                        self.carte.redessiner()
                if event.type == pygame.KEYUP:
                    if event.key == DECALER_GAUCHE:
                        self.mouvement_x[0] = False
                    if event.key == DECALER_DROITE:
                        self.mouvement_x[1] = False
                    if event.key == DECALER_HAUT:
                        self.mouvement_y[0] = False
                    if event.key == DECALER_BAS:
                        self.mouvement_y[1] = False

            self.carte.afficher(self.affichage, self.decalage)
            self.ecran.blit(pygame.transform.scale(self.affichage, TAILLE_ECRAN), (0, 0))
            debogage.deboguer(f"Haut : {self.p_haut * 100:.2f}%")
            debogage.deboguer(f"Gauche : {self.p_gauche * 100:.2f}%", x = 150)
            debogage.deboguer(f"Bas : {(1-self.p_haut) * 100:.2f}%", y=20)
            debogage.deboguer(f"Droite : {(1-self.p_gauche) * 100:.2f}%", x = 150,y=20)
            pygame.display.update()
            self.horloge.tick(60)

    def appliquer_decalage(self):
        self.decalage.x += (self.mouvement_x[1] - self.mouvement_x[0]) * 5
        self.decalage.y += (self.mouvement_y[1] - self.mouvement_y[0]) * 5

    def tout_effacer(self) -> None:
        self.carte.carte = {}


Editeur().lancer()
