from typing import Any, NoReturn
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
        self.ecran = pygame.display.set_mode(TAILLE_ECRAN, pygame.SRCALPHA)
        self.rsc: dict[str, Any] = {
            'herbe': charger_images("rsc/herbe"),
        }
        self.horloge = pygame.time.Clock()
        self.decalage: pygame.Vector2 = pygame.Vector2()
        self.carte = Carte(self)

        # Pour la disposition des tuiles
        self.mouvement_x: list[int] = [0, 0]
        self.mouvement_y: list[int] = [0, 0]

        self.generation_procedurale()

    def generation_procedurale(self):
        x = n_x = 0
        y = n_y = 0
        self.p_haut: float = random.random()
        self.p_gauche: float = random.random()
        for _ in range(500):
            while self.carte.tuile_presente((n_x, n_y)):
                if random.random() < self.p_gauche:
                    n_x += DEC_GAUCHE[0]
                else:
                    n_x += DEC_DROITE[0]
                if random.random() < self.p_haut:
                    n_y += DEC_HAUT[1]
                else:
                    n_y += DEC_BAS[1]
            x = n_x
            y = n_y
            self.carte.ajouter_tuile(x, y)
        self.remplir()
        self.carte.redessiner()

    def remplir(self):
        """Cette fonction mets des tuiles dans les espaces vides et fermés de la carte"""
        for tuile in self.carte.carte.copy().values():
            self.carte.entourer(tuile)

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
                        self.generation_procedurale()
                    if event.key == DECALER_GAUCHE:
                        self.mouvement_x[0] = True
                    if event.key == DECALER_DROITE:
                        self.mouvement_x[1] = True
                    if event.key == DECALER_HAUT:
                        self.mouvement_y[0] = True
                    if event.key == DECALER_BAS:
                        self.mouvement_y[1] = True
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
            debogage.deboguer(f"Il y a {self.p_haut*100:.2f}% de chance que le chemin monte", couleur="yellow")
            debogage.deboguer(f"Il y a {self.p_gauche*100:.2f}% de chance que le chemin vire vers la gauche", couleur="yellow", y = 20)
            pygame.display.update()
            self.horloge.tick(60)

    def appliquer_decalage(self):
        self.decalage.x += (self.mouvement_x[1] - self.mouvement_x[0]) * 5
        self.decalage.y += (self.mouvement_y[1] - self.mouvement_y[0]) * 5

    def tout_effacer(self):
        self.carte.carte = {}


Editeur().lancer()
