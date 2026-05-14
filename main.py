"""Point d'entrée principal du générateur procédural de cartes."""

from typing import Callable, NoReturn, Optional
import pygame
import random
import sys
from scripts.carte import Carte
from scripts.rendu.camera import Rendu
from scripts.type import TypeTuile
from scripts.utilitaires import debogage
from scripts.utilitaires.outils_images import charger_images
from scripts.parametres import DECALAGE_BAS, DECALAGE_DROITE, DECALAGE_GAUCHE, DECALAGE_HAUT, DECALER_BAS, DECALER_DROITE, DECALER_GAUCHE, DECALER_HAUT, FPS, GENERER_CARTE, GENERER_CARTE_ILES, NOMBRE_TUILES, TAILLE_AFFICHAGE, TAILLE_ECRAN, VITESSE_CAMERA
# Tester avec stubtest.exe


class GenerateurProcedural:
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
            "plante": charger_images("rsc/images/deco/plantes"),
            "arbre": charger_images("rsc/images/deco/arbres"),
        }
        self.horloge = pygame.time.Clock()
        self.camera = Rendu(*TAILLE_ECRAN)
        self.carte = Carte({"herbe" : self.ressources["herbe"], "pierre": self.ressources["pierre"]}, {"plante": self.ressources["plante"], "arbre": self.ressources["arbre"]})

        # Pour les messages de débogage
        self.message_debug: Optional[str] = None
        self.couleur_debug: Optional[pygame.Color] = None

        # Pour la disposition des tuiles
        self.mouvement_horizontal: list[bool] = [False, False]
        self.mouvement_vertical: list[bool] = [False, False]

        # Pour la génération procédurale
        self.nombre_tuiles: int = NOMBRE_TUILES
        self.probabilite_monter: float = 0.0
        self.probabilite_gauche: float = 0.0

        self.generer_carte(self.generation_procedurale_iles)

    def generer_carte(self, fonction: Callable[..., None]) -> None:
        """Génère une nouvelle carte en utilisant la fonction de génération spécifiée.

        Args:
            fonction (Callable[..., None]): Fonction de génération à utiliser.
        """
        self.effacer_tuiles()
        fonction()
        self.carte.remplir()
        self.carte.redessiner()
        self.carte.generer_deco()
        # Mettre à jour les tuiles et décorations dans la caméra
        self.camera.empty()
        self.camera.add(self.carte.tuiles)
        self.camera.add(self.carte.deco)

    def generation_procedurale_bloc(self) -> None:
        """Génère une carte procédurale avec un chemin continu.

        Crée un chemin aléatoire en plaçant des tuiles selon des probabilités
        de direction (gauche/droite, haut/bas) définies aléatoirement.
        """
        position_x = nouvelle_position_x = 0.0
        position_y = nouvelle_position_y = 0.0
        self.probabilite_monter, self.probabilite_gauche = random.choice([
            (0.8, 0.8), (0.8, 0.2), (0.2, 0.8), (0.2, 0.2)
        ])
        for _ in range(self.nombre_tuiles):
            while self.carte.tuile_presente((nouvelle_position_x, nouvelle_position_y)):
                if random.random() < self.probabilite_gauche:
                    nouvelle_position_x += DECALAGE_GAUCHE[0] * 16
                else:
                    nouvelle_position_x += DECALAGE_DROITE[0] * 16
                if random.random() < self.probabilite_monter:
                    nouvelle_position_y += DECALAGE_HAUT[1] * 16
                else:
                    nouvelle_position_y += DECALAGE_BAS[1] * 16
            position_x: float = nouvelle_position_x
            position_y: float = nouvelle_position_y
            self.carte.ajouter_tuile((position_x, position_y), "herbe")

    def generation_procedurale_iles(self) -> None:
        """Génère des îles variées séparées par des espaces vides.

        Crée différentes formes d'îles (triangles, ponts, escaliers, rectangles)
        de tailles et types variés, séparées par 1 à 4 tuiles vides.
        Les îles sont moins nombreuses mais plus grandes et praticables.
        """
        position_x = 0.0
        limite_horizontale: float = self.nombre_tuiles * 16

        formes: list[str] = [
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

            # Définition des tailles selon la forme en pixels
            match forme:
                case "escalier":
                    largeur: float = random.randint(32, 64)
                    hauteur: float = random.randint(32, 48)
                case "rectangle":
                    # Rectangles plus larges et plus hauts
                    largeur = random.choice([
                        random.randint(80, 160),
                        random.randint(160, 320)
                    ])
                    hauteur = random.choice([random.randint(48, 112)])
                case _:
                    largeur = random.randint(64, 128)
                    hauteur = random.randint(32, 64)

            # Détermine la hauteur de base en évitant les superpositions
            hauteur_base: float = self.carte._hauteur_libre(position_x, largeur)

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
            espace_vide: float = random.randint(1, 4) * 16
            position_x += largeur + espace_vide

    def lancer(self) -> NoReturn:
        """Boucle principale du jeu gérant les événements et l'affichage."""
        while True:
            self.fenetre.fill((0, 0, 0))
            self.surface_affichage.fill((0, 0, 0))
            self.appliquer_decalage()
            self._gerer_evenements()

            # Utiliser la caméra pour le rendu avec optimisation des tuiles visibles
            self.camera.draw(self.surface_affichage)
            self.fenetre.blit(pygame.transform.scale(self.surface_affichage, TAILLE_ECRAN), (0, 0))
            # Affichage du nom de la carte en mode débogage
            nom_affiche: str = self.carte.nom_fichier if self.carte.nom_fichier else "Nouvelle carte"
            debogage.afficher_debug(self.fenetre, nom_affiche, couleur=pygame.Color("yellow"), alignement=pygame.FONT_CENTER)
            debogage.afficher_debug(self.fenetre, f"Haut : {self.probabilite_monter * 100:.2f}%")
            debogage.afficher_debug(self.fenetre, f"Gauche : {self.probabilite_gauche * 100:.2f}%", x=150)
            debogage.afficher_debug(self.fenetre, f"Bas : {(1-self.probabilite_monter) * 100:.2f}%", y=20)
            debogage.afficher_debug(self.fenetre, f"Droite : {(1-self.probabilite_gauche) * 100:.2f}%", x=150, y=20)
            debogage.afficher_debug(self.fenetre, self.carte.tuiles, y=40)
            # Affichage des messages de débogage pour les opérations de fichier
            if self.message_debug and self.couleur_debug:
                debogage.afficher_debug(self.fenetre, self.message_debug, y=60, couleur=self.couleur_debug)
            pygame.display.update()

            self.horloge.tick(FPS)

    def _gerer_evenements(self) -> None:
        """Gère les événements Pygame dans la boucle principale."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self._gerer_appui_touche(event.key)
            if event.type == pygame.KEYUP:
                self._gerer_relachement_touche(event.key)

    def _gerer_appui_touche(self, key: int) -> None:
        """Gère les événements de touche pressée."""
        if key == GENERER_CARTE_ILES:
            self.camera.decalage = pygame.Vector2()
            self.generer_carte(self.generation_procedurale_iles)
        elif key == GENERER_CARTE:
            self.camera.decalage = pygame.Vector2()
            self.generer_carte(self.generation_procedurale_bloc)
        elif key == DECALER_GAUCHE:
            self.mouvement_horizontal[0] = True
        elif key == DECALER_DROITE:
            self.mouvement_horizontal[1] = True
        elif key == DECALER_HAUT:
            self.mouvement_vertical[0] = True
        elif key == DECALER_BAS:
            self.mouvement_vertical[1] = True
        elif key == pygame.K_o:
            succes, message = self.carte.charger_carte()
            if succes:
                # Mettre à jour les tuiles et décorations dans la caméra
                self.camera.empty()
                self.camera.add(self.carte.tuiles)
                self.camera.add(self.carte.deco)
            self.message_debug = f"✓ {message}" if succes else f"✗ {message}"
            self.couleur_debug = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
        elif key == pygame.K_s:
            succes, message = self.carte.enregistrer_carte()
            self.message_debug = f"✓ {message}" if succes else f"✗ {message}"
            self.couleur_debug = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
        elif key == pygame.K_n:
            succes, message = self.carte.nouvelle_carte()
            if succes:
                # Mettre à jour les tuiles et décorations dans la caméra
                self.camera.empty()
                self.camera.add(self.carte.tuiles)
                self.camera.add(self.carte.deco)
            self.message_debug = f"✓ {message}" if succes else f"✗ {message}"
            self.couleur_debug = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)

    def _gerer_relachement_touche(self, key: int) -> None:
        """Gère les événements de touche relâchée."""
        if key == DECALER_GAUCHE:
            self.mouvement_horizontal[0] = False
        elif key == DECALER_DROITE:
            self.mouvement_horizontal[1] = False
        elif key == DECALER_HAUT:
            self.mouvement_vertical[0] = False
        elif key == DECALER_BAS:
            self.mouvement_vertical[1] = False

    def appliquer_decalage(self) -> None:
        """Applique le décalage de la caméra selon les mouvements."""
        dx = (self.mouvement_horizontal[1] - self.mouvement_horizontal[0]) * VITESSE_CAMERA
        dy = (self.mouvement_vertical[1] - self.mouvement_vertical[0]) * VITESSE_CAMERA
        self.camera.deplacer(dx, dy)

    def effacer_tuiles(self) -> None:
        """Efface toutes les tuiles de la carte actuelle."""
        self.carte = Carte(self.carte.images_tuiles, self.carte.images_deco)


GenerateurProcedural().lancer()
