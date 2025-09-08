from typing import Any, Callable, Literal, NoReturn, Optional
import pygame
import random
from scripts.carte import Carte
from scripts.type import TypeTuile
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
            'herbe': charger_images("rsc/images/tuiles/herbe"),
            'pierre': charger_images("rsc/images/tuiles/pierre"),
        }
        self.horloge = pygame.time.Clock()
        self.decalage: pygame.Vector2 = pygame.Vector2()
        self.carte = Carte(self)

        # Pour les messages de débogage
        self.debug_message: Optional[str] = None
        self.debug_color: Optional[pygame.Color] = None

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
            self.carte.ajouter_tuile(x, y, "herbe")
        self.carte.redessiner()

    def generation_procedurale_iles(self) -> None:
        """
        Génère des îles variées (triangles, ponts, escaliers, rectangles), séparées par 1 à 4 vides.
        Les îles sont moins nombreuses, plus grandes et praticables.
        """
        x = 0
        max_x = self.nb_tuiles  # limite horizontale

        formes = [
            "triangle_inversé",
            "triangle_normal",
            "pont",
            "triangle_vertical",
            "escalier",
            "rectangle"
        ]

        while x < max_x:
            forme: str = random.choice(formes)
            type_tuile: TypeTuile = random.choice(("herbe", "pierre"))

            # Définition des tailles selon la forme
            match forme:
                case "escalier":
                    largeur: int = random.randint(2, 4)
                    hauteur: int = random.randint(2, 3)
                case "rectangle":
                    largeur = random.choice([random.randint(5, 10), random.randint(10, 20)])  # rectangles plus larges
                    hauteur = random.choice([random.randint(3, 7)])   # rectangles plus hauts
                case _:
                    largeur = random.randint(4, 8)
                    hauteur = random.randint(2, 4)

            # Détermine la hauteur de base en évitant les superpositions
            y_base = self.carte._hauteur_libre(x, largeur)

            # Crée la forme
            match forme:
                case "triangle_inversé":
                    self.carte._creer_triangle_inverse(x, y_base, largeur, hauteur, type_tuile)
                case "triangle_normal":
                    self.carte._creer_triangle_normal(x, y_base, hauteur, type_tuile)
                case "pont":
                    self.carte._creer_pont(x, y_base, largeur, type_tuile)
                case "triangle_vertical":
                    self.carte._creer_triangle_vertical(x, y_base, largeur, hauteur, type_tuile)
                case "escalier":
                    self.carte._creer_escalier(x, y_base, hauteur, type_tuile)
                case "rectangle":
                    self.carte._creer_rectangle(x, y_base, largeur, hauteur, type_tuile)

            # Décalage horizontal pour la prochaine île
            espace_vide: int = random.randint(1, 4)
            x += largeur + espace_vide

        self.carte.redessiner()

    fonc_generation_procedurale: Callable[..., None] = generation_procedurale_iles

    def lancer(self) -> NoReturn:
        while True:
            self.ecran.fill((0, 0, 0))
            self.affichage.fill((0, 0, 0))
            self.appliquer_decalage()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == GENERER_CARTE_ILES:
                        self.decalage = pygame.Vector2()
                        self.tout_effacer()
                        self.generation_procedurale_iles()
                    if event.key == GENERER_CARTE:
                        self.decalage = pygame.Vector2()
                        self.tout_effacer()
                        self.generation_procedurale()
                        self.carte.remplir()
                        self.carte.redessiner()
                    if event.key == DECALER_GAUCHE:
                        self.mouvement_x[0] = True
                    if event.key == DECALER_DROITE:
                        self.mouvement_x[1] = True
                    if event.key == DECALER_HAUT:
                        self.mouvement_y[0] = True
                    if event.key == DECALER_BAS:
                        self.mouvement_y[1] = True
                    if event.key == pygame.K_o:
                        succes, message = self.carte.charger_carte()
                        self.debug_message = f"✓ {message}" if succes else f"✗ {message}"
                        self.debug_color = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
                    if event.key == pygame.K_s:
                        succes, message = self.carte.enreg_carte()
                        self.debug_message = f"✓ {message}" if succes else f"✗ {message}"
                        self.debug_color = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
                    if event.key == pygame.K_n:
                        succes, message = self.carte.nouvelle_carte()
                        self.debug_message = f"✓ {message}" if succes else f"✗ {message}"
                        self.debug_color = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
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
            # Affichage du nom de la carte en mode débogage
            nom_affiche: str = self.carte.nom_fichier if self.carte.nom_fichier else "Nouvelle carte"
            debogage.deboguer(nom_affiche, couleur=pygame.Color("yellow"), alignement=pygame.FONT_CENTER)
            debogage.deboguer(f"Haut : {self.p_haut * 100:.2f}%")
            debogage.deboguer(f"Gauche : {self.p_gauche * 100:.2f}%", x = 150)
            debogage.deboguer(f"Bas : {(1-self.p_haut) * 100:.2f}%", y=20)
            debogage.deboguer(f"Droite : {(1-self.p_gauche) * 100:.2f}%", x = 150,y=20)
            # Affichage des messages de débogage pour les opérations de fichier
            if self.debug_message and self.debug_color:
                debogage.deboguer(self.debug_message, y=40, couleur=self.debug_color)
            pygame.display.update()
            
            self.horloge.tick(60)

    def appliquer_decalage(self):
        self.decalage.x += (self.mouvement_x[1] - self.mouvement_x[0]) * 5
        self.decalage.y += (self.mouvement_y[1] - self.mouvement_y[0]) * 5

    def tout_effacer(self) -> None:
        self.carte.carte = {}


Editeur().lancer()
