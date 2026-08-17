"""Point d'entrée principal du générateur procédural de cartes."""

from typing import Literal, NoReturn, Optional
import pygame
import sys

from scripts.generation import generer_carte
from scripts.parametres.type import TypeDecoration, TypeEntite, TypeTuile
from scripts.rendu import Rendu
from scripts.utilitaires import debogage
from scripts.parametres import DECALER_BAS, DECALER_DROITE, DECALER_GAUCHE, DECALER_HAUT, ENREGISTRER_CARTE, FPS, GENERER_CARTE, GENERER_CARTE_ILES, NOUVELLE_CARTE, OUVRIR_CARTE, TAILLE_AFFICHAGE, TAILLE_ECRAN, VITESSE_CAMERA
from scripts.utilitaires.outils_images import charger_image, charger_images
# Tester avec stubtest.exe


class Fenetre:
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

        self.ressources: dict[str, list[pygame.Surface] | pygame.Surface] = {
            # Décor
            'herbe': charger_images("rsc/images/tuiles/herbe"),
            'pierre': charger_images("rsc/images/tuiles/pierre"),
            "plante": charger_images("rsc/images/deco/plantes"),
            "arbre": charger_images("rsc/images/deco/arbres"),

            # Entités
            "joueur": charger_image("rsc/images/personnages/joueur/joueur.png"),
            "ennemi": charger_image("rsc/images/personnages/ennemi/ennemi.png")
        }

        self.horloge = pygame.time.Clock()

        images_tuiles: dict[TypeTuile, list[pygame.Surface]]= {"herbe" : self.ressources["herbe"], "pierre": self.ressources["pierre"]} # pyright: ignore[reportAssignmentType]
        images_deco: dict[TypeDecoration, list[pygame.Surface]] = {"plante": self.ressources["plante"], "arbre": self.ressources["arbre"]} # pyright: ignore[reportAssignmentType]
        images_entites: dict[TypeEntite, pygame.Surface]= {"joueur": self.ressources["joueur"], "ennemi": self.ressources["ennemi"]} # pyright: ignore[reportAssignmentType]
        self.groupes_images: tuple[dict[TypeTuile | TypeDecoration | TypeEntite, list[pygame.Surface]] | pygame.Surface, ...] = (images_tuiles, images_deco, images_entites) # pyright: ignore[reportAttributeAccessIssue]

        # Mettre à jour les tuiles et décorations dans la caméra
        self.camera = Rendu(*TAILLE_ECRAN)

        self.nouvelle_generation("Ile")

        # Pour les messages de débogage
        self.message_debug: Optional[str] = None
        self.couleur_debug: Optional[pygame.Color] = None

        # Pour la disposition des tuiles
        self.mouvement_horizontal: list[bool] = [False, False]
        self.mouvement_vertical: list[bool] = [False, False]

    def nouvelle_generation(self, type_terrain: Literal["Ile", "Bloc"]) -> None:
        self.carte = generer_carte(type_terrain, *self.groupes_images) # pyright: ignore[reportArgumentType]

        self.camera.empty()
        self.camera.add(self.carte.carte_tuiles.values())
        self.camera.add(self.carte.carte_deco.values())
        self.camera.add(self.carte.carte_entites.values())


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
            # debogage.afficher_debug(self.fenetre, self.carte.carte_tuiles.values(), y=40)
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
            self.nouvelle_generation("Ile")
        elif key == GENERER_CARTE:
            self.camera.decalage = pygame.Vector2()
            self.nouvelle_generation("Bloc")
        elif key == DECALER_GAUCHE:
            self.mouvement_horizontal[0] = True
        elif key == DECALER_DROITE:
            self.mouvement_horizontal[1] = True
        elif key == DECALER_HAUT:
            self.mouvement_vertical[0] = True
        elif key == DECALER_BAS:
            self.mouvement_vertical[1] = True
        elif key == OUVRIR_CARTE:
            succes, message = self.carte.charger_carte()
            if succes:
                # Mettre à jour les tuiles et décorations dans la caméra
                self.camera.empty()
                self.camera.add(self.carte.carte_tuiles.values())
                self.camera.add(self.carte.carte_deco.values())
            self.message_debug = f"✓ {message}" if succes else f"✗ {message}"
            self.couleur_debug = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
        elif key == ENREGISTRER_CARTE:
            succes, message = self.carte.enregistrer_carte()
            self.message_debug = f"✓ {message}" if succes else f"✗ {message}"
            self.couleur_debug = pygame.Color(0, 255, 0) if succes else pygame.Color(255, 0, 0)
        elif key == NOUVELLE_CARTE:
            succes, message = self.carte.nouvelle_carte()
            if succes:
                # Mettre à jour les tuiles et décorations dans la caméra
                self.camera.empty()
                self.camera.add(self.carte.carte_tuiles.values())
                self.camera.add(self.carte.carte_deco.values())
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


Fenetre().lancer()
