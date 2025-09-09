"""Point d'entrée principal du générateur procédural de cartes."""

from typing import Any, Callable, NoReturn, Optional
import pygame
import random
from scripts.carte import Carte
from scripts.type import TypeTuile
from scripts.utilitaires import debogage
from scripts.utilitaires.outils_images import charger_images
from scripts.parametres import *
# Tester avec stubtest.exe


class Editeur:
    """Éditeur principal pour la génération et l'affichage de cartes procédurales.

    Cette classe gère l'initialisation de Pygame, le chargement des ressources,
    la génération procédurale de cartes et la boucle principale du jeu.
    """

    def __init__(self) -> None:
        """Initialise l'éditeur Pygame et génère la première carte."""
        pygame.init()
        pygame.display.set_caption("Éditeur de niveau")

        # Pour l'affichage
        self.surface_affichage = pygame.Surface(TAILLE_AFFICHAGE)
        self.fenetre: pygame.Surface = pygame.display.set_mode(TAILLE_ECRAN, pygame.SRCALPHA)
        self.ressources: dict[str, list[pygame.Surface]] = {
            'herbe': charger_images("rsc/images/tuiles/herbe"),
            'pierre': charger_images("rsc/images/tuiles/pierre"),
        }
        self.horloge_jeu = pygame.time.Clock()
        self.decalage_camera: pygame.Vector2 = pygame.Vector2()
        self.carte = Carte(self)

        # Pour les messages de débogage
        self.message_debug: Optional[str] = None
        self.couleur_debug: Optional[pygame.Color] = None

        # Pour la disposition des tuiles
        self.mouvement_horizontal: list[bool] = [False, False]
        self.mouvement_vertical: list[bool] = [False, False]

        # Pour la génération procédurale
        NOMBRE_TUILES_DEFAUT = 500
        self.nombre_tuiles: int = NOMBRE_TUILES_DEFAUT
        self.probabilite_monter: float = 0.0
        self.probabilite_gauche: float = 0.0

        # Pour les performances
        self.fps_defaut = 60

        # Pour les contrôles
        self.vitesse_camera = 5

        self.generation_procedurale_iles()

    def generation_procedurale(self) -> None:
        """Génère une carte procédurale avec un chemin continu.

        Crée un chemin aléatoire en plaçant des tuiles selon des probabilités
        de direction (gauche/droite, haut/bas) définies aléatoirement.
        """
        position_x = nouvelle_position_x = 0
        position_y = nouvelle_position_y = 0
        self.probabilite_monter, self.probabilite_gauche = random.choice([
            (0.8, 0.8), (0.8, 0.2), (0.2, 0.8), (0.2, 0.2)
        ])
        for _ in range(self.nombre_tuiles):
            while self.carte.tuile_presente((nouvelle_position_x, nouvelle_position_y)):
                if random.random() < self.probabilite_gauche:
                    nouvelle_position_x += DECALAGE_GAUCHE[0]
                else:
                    nouvelle_position_x += DECALAGE_DROITE[0]
                if random.random() < self.probabilite_monter:
                    nouvelle_position_y += DECALAGE_HAUT[1]
                else:
                    nouvelle_position_y += DECALAGE_BAS[1]
            position_x = nouvelle_position_x
            position_y = nouvelle_position_y
            self.carte.ajouter_tuile(position_x, position_y, "herbe")
        self.carte.redessiner()

    def generation_procedurale_iles(self) -> None:
        """Génère des îles variées séparées par des espaces vides.

        Crée différentes formes d'îles (triangles, ponts, escaliers, rectangles)
        de tailles et types variés, séparées par 1 à 4 tuiles vides.
        Les îles sont moins nombreuses mais plus grandes et praticables.
        """
        position_x = 0
        limite_horizontale = self.nombre_tuiles

        formes = [
            "triangle_inversé",
            "triangle_normal",
            "pont",
            "triangle_vertical",
            "escalier",
            "rectangle"
        ]

        while position_x < limite_horizontale:
            forme: str = random.choice(formes)
            type_tuile: TypeTuile = random.choice(("herbe", "pierre"))

            # Définition des tailles selon la forme
            match forme:
                case "escalier":
                    largeur: int = random.randint(2, 4)
                    hauteur: int = random.randint(2, 3)
                case "rectangle":
                    # Rectangles plus larges et plus hauts
                    largeur = random.choice([
                        random.randint(5, 10),
                        random.randint(10, 20)
                    ])
                    hauteur = random.choice([random.randint(3, 7)])
                case _:
                    largeur = random.randint(4, 8)
                    hauteur = random.randint(2, 4)

            # Détermine la hauteur de base en évitant les superpositions
            hauteur_base = self.carte._hauteur_libre(position_x, largeur)

            # Crée la forme
            match forme:
                case "triangle_inversé":
                    self.carte._creer_triangle_inverse(position_x, hauteur_base, largeur, hauteur, type_tuile)
                case "triangle_normal":
                    self.carte._creer_triangle_normal(position_x, hauteur_base, hauteur, type_tuile)
                case "pont":
                    self.carte._creer_pont(position_x, hauteur_base, largeur, type_tuile)
                case "triangle_vertical":
                    self.carte._creer_triangle_vertical(position_x, hauteur_base, largeur, hauteur, type_tuile)
                case "escalier":
                    self.carte._creer_escalier(position_x, hauteur_base, hauteur, type_tuile)
                case "rectangle":
                    self.carte._creer_rectangle(position_x, hauteur_base, largeur, hauteur, type_tuile)

            # Décalage horizontal pour la prochaine île
            espace_vide: int = random.randint(1, 4)
            position_x += largeur + espace_vide

        self.carte.redessiner()

    fonc_generation_procedurale: Callable[..., None] = generation_procedurale_iles

    def lancer(self) -> NoReturn:
        """Boucle principale du jeu gérant les événements et l'affichage."""
        while True:
            self.fenetre.fill((0, 0, 0))
            self.surface_affichage.fill((0, 0, 0))
            self.appliquer_decalage()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == GENERER_CARTE_ILES:
                        self.decalage_camera = pygame.Vector2()
                        self.tout_effacer()
                        self.generation_procedurale_iles()
                    if event.key == GENERER_CARTE:
                        self.decalage_camera = pygame.Vector2()
                        self.tout_effacer()
                        self.generation_procedurale()
                        self.carte.remplir()
                        self.carte.redessiner()
                    if event.key == DECALER_GAUCHE:
                        self.mouvement_horizontal[0] = True
                    if event.key == DECALER_DROITE:
                        self.mouvement_horizontal[1] = True
                    if event.key == DECALER_HAUT:
                        self.mouvement_vertical[0] = True
                    if event.key == DECALER_BAS:
                        self.mouvement_vertical[1] = True
                    if event.key == pygame.K_o:
                        succes, message = self.carte.charger_carte()
                        self.message_debug = f"✓ {message}" if succes else f"✗ {message}"
                        self.couleur_debug = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
                    if event.key == pygame.K_s:
                        succes, message = self.carte.enregistrer_carte()
                        self.message_debug = f"✓ {message}" if succes else f"✗ {message}"
                        self.couleur_debug = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
                    if event.key == pygame.K_n:
                        succes, message = self.carte.nouvelle_carte()
                        self.message_debug = f"✓ {message}" if succes else f"✗ {message}"
                        self.couleur_debug = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
                if event.type == pygame.KEYUP:
                    if event.key == DECALER_GAUCHE:
                        self.mouvement_horizontal[0] = False
                    if event.key == DECALER_DROITE:
                        self.mouvement_horizontal[1] = False
                    if event.key == DECALER_HAUT:
                        self.mouvement_vertical[0] = False
                    if event.key == DECALER_BAS:
                        self.mouvement_vertical[1] = False

            self.carte.afficher(self.surface_affichage, self.decalage_camera)
            self.fenetre.blit(pygame.transform.scale(self.surface_affichage, TAILLE_ECRAN), (0, 0))
            # Affichage du nom de la carte en mode débogage
            nom_affiche: str = self.carte.nom_fichier if self.carte.nom_fichier else "Nouvelle carte"
            debogage.afficher_debug(nom_affiche, couleur=pygame.Color("yellow"), alignement=pygame.FONT_CENTER)
            debogage.afficher_debug(f"Haut : {self.probabilite_monter * 100:.2f}%")
            debogage.afficher_debug(f"Gauche : {self.probabilite_gauche * 100:.2f}%", x=150)
            debogage.afficher_debug(f"Bas : {(1-self.probabilite_monter) * 100:.2f}%", y=20)
            debogage.afficher_debug(f"Droite : {(1-self.probabilite_gauche) * 100:.2f}%", x=150, y=20)
            # Affichage des messages de débogage pour les opérations de fichier
            if self.message_debug and self.couleur_debug:
                debogage.afficher_debug(self.message_debug, y=40, couleur=self.couleur_debug)
            pygame.display.update()

            self.horloge_jeu.tick(self.fps_defaut)

    def appliquer_decalage(self) -> None:
        """Applique le décalage de la caméra selon les mouvements."""
        self.decalage_camera.x += (self.mouvement_horizontal[1] - self.mouvement_horizontal[0]) * self.vitesse_camera
        self.decalage_camera.y += (self.mouvement_vertical[1] - self.mouvement_vertical[0]) * self.vitesse_camera

    def tout_effacer(self) -> None:
        """Efface toutes les tuiles de la carte actuelle."""
        self.carte.carte = {}


Editeur().lancer()
