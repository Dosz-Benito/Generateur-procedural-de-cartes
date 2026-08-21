import random
from typing import Any, Generator, Literal
from warnings import deprecated
import pygame
from ..carte import HAUTEUR_MAX_GENERATION, HAUTEUR_MIN_GENERATION, Carte
from ..parametres import DECALAGE_BAS, DECALAGE_DROITE, DECALAGE_GAUCHE, DECALAGE_HAUT, TypeTuile
from ..parametres.type import TypeDecoration, TypeEntite
from ..tuile import Tuile, Entite
from ..parametres import images_tuiles, images_deco, images_entites


class GenerateurCarte:
    def __init__(self, nombre_tuiles_max_horizontal: int, longueur_tuile: int = 16, largeur_tuile: int = 16, ) -> None:
        self.nombre_tuiles: int = nombre_tuiles_max_horizontal
        self.longueur_tuile: int = longueur_tuile
        self.largeur_tuile: int = largeur_tuile

        # ! A supprimer avec la fonction self.generation_procedurale_bloc
        self.probabilite_monter: float = 0.0
        self.probabilite_gauche: float = 0.0

    def generer(self, type_terrain: Literal["Ile", "Bloc"]) -> Carte:
        """Génère la carte selon le type de génération demandé.

        Args:
            type_terrain (Literal["Ile", "Bloc"]): Type de génération à utiliser pour le terrain.
        """
        # carte = Carte(images_tuiles, images_deco, images_entites) # pyright: ignore[reportArgumentType]
        carte = Carte(images_tuiles, images_deco, images_entites)
        match type_terrain:
            case "Ile":
                self.generer_terrain_en_iles(carte)
            case "Bloc":
                self.generation_procedurale_bloc()
            case _:
                raise ValueError(f"Le type de carte {type_terrain} n'est pas pris en charge")
        carte.remplir()
        carte.redessiner()
        carte.definir_groupes_tuiles()
        self.generer_deco(carte)
        self.generer_entite("joueur", carte)
        self.generer_entite("ennemi", carte)
        return carte

    # region Génération du terrain
    @deprecated("La fonction est à revoir")
    def generation_procedurale_bloc(self) -> None:
        """Génère une carte procédurale avec un chemin continu.

        Crée un chemin aléatoire en plaçant des tuiles selon des probabilités
        de direction (gauche/droite, haut/bas) définies aléatoirement.
        """
        raise NotImplementedError
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

    def generer_terrain_en_iles(self, carte: Carte) -> None:
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
            hauteur_base: float = self._hauteur_libre(position_x, largeur, carte)

            # Crée la forme
            match forme:
                case "triangle_inversé":
                    for pos_tuile in self._creer_triangle_inverse(position_x, hauteur_base, largeur, hauteur):
                        carte.ajouter_tuile(pos_tuile, type_tuile)
                case "triangle_normal":
                    for pos_tuile in self._creer_triangle_normal(position_x, hauteur_base, hauteur):
                        carte.ajouter_tuile(pos_tuile, type_tuile)
                case "pont":
                    for pos_tuile in self._creer_pont(position_x, hauteur_base, largeur):
                        carte.ajouter_tuile(pos_tuile, type_tuile)
                case "triangle_vertical":
                    for pos_tuile in self._creer_triangle_vertical(position_x, hauteur_base, largeur, hauteur):
                        carte.ajouter_tuile(pos_tuile, type_tuile)
                case "escalier":
                    for pos_tuile in self._creer_escalier(position_x, hauteur_base, hauteur):
                        carte.ajouter_tuile(pos_tuile, type_tuile)
                case "rectangle":
                    for pos_tuile in self._creer_rectangle(position_x, hauteur_base, largeur, hauteur):
                        carte.ajouter_tuile(pos_tuile, type_tuile)

            # Décalage horizontal pour la prochaine île
            espace_vide: float = random.randint(1, 4) * 16
            position_x += largeur + espace_vide
    # endregion

    # region Génération de la décoration
    def generer_deco(self, carte: Carte) -> None:
        """Génère des décorations aléatoires sur les tuiles existantes."""
        for tuile in carte.tuiles_marchables:
            if random.random() < 0.5:
                type_deco: TypeDecoration = random.choice(list(carte.images_deco.keys()))
                index = random.choice(range(len(carte.images_deco[type_deco])))
                image = carte.images_deco[type_deco][index].copy()
                rect = image.get_frect(midbottom = tuile.rect.midtop)
                carte.ajouter_deco(rect, type_deco, index)
    # endregion

    # region Génération des entités
    def generer_entite(self, type_entite: TypeEntite, carte: Carte) -> None:
        match type_entite:
            case "joueur":
                self.generer_joueur(carte)
            case "ennemi":
                self.generer_ennemis(carte)
            case _:
                raise ValueError(f"Le type d'entité {type_entite} n'est pas pris en charge")

    def generer_joueur(self, carte: Carte) -> None:
        tuile_choisie: Tuile = carte.tuiles_marchables.sprites()[0]
        
        resultat_tuile_en_haut: list[Tuile] = carte._tuiles_autour(tuile_choisie, [DECALAGE_HAUT])
        while len(resultat_tuile_en_haut) != 0:
            tuile_choisie = resultat_tuile_en_haut[0]
            resultat_tuile_en_haut = carte._tuiles_autour(tuile_choisie, [DECALAGE_HAUT])

        image_joueur = carte.images_entites["joueur"]
        rect_joueur = image_joueur.get_frect()
        rect_joueur.bottomleft = tuile_choisie.rect.topleft
        rect_joueur.bottom -= 16*5
        carte.carte_entites["joueur"] = Entite("joueur", rect_joueur.topleft, image_joueur)

    def generer_ennemis(self, carte: Carte) -> None:
            carte.carte_entites["ennemi"] = []
            for bloc in carte._extraire_blocs_tuiles_marchables(3):
                tuile_choisie: Tuile = min(bloc.tuiles, key=lambda tuile: abs(tuile.rect.x - bloc.milieu))
                for i in range(random.randint(0, bloc.nb_tuiles)):
                    carte.carte_entites["ennemi"].append(Entite("ennemi", carte.images_entites["ennemi"].get_frect(left=tuile_choisie.rect.left, bottom=tuile_choisie.rect.top - 16*5).topleft, carte.images_entites["ennemi"])) # pyright: ignore[reportAttributeAccessIssue]
    # endregion

    #region Génération des îles
    def _creer_triangle_inverse(self, x_base_gauche: float, y_base: float, largeur: float, hauteur: float) -> Generator[tuple[float, float], Any, None]:
        """
        Crée une île en forme de triangle inversé (pyramide renversée).

        Args:
            x_base_gauche (float): Coordonnée X du coin en bas à gauche de la pyramide en pixels
            y_base (float): Coordonnée Y du coin en bas à gauche de la pyramide en pixels
            largeur (float): Largeur de la base du triangle en pixels
            hauteur (float): Hauteur du triangle en pixels
        """
        niveaux = int(hauteur / 16)
        largeur_tuiles = int(largeur / 16)
        for niveau in range(niveaux):
            for decalage_x in range(largeur_tuiles - 2 * niveau):
                yield (x_base_gauche + decalage_x * 16 + niveau * 16, y_base - niveau * 16)

    def _creer_triangle_normal(self, x_base_gauche: float, y_base: float, hauteur: float) -> Generator[tuple[float, float], Any, None]:
        """
        Crée une île en forme de triangle normal (pyramide classique).

        Args:
            x_base_gauche (float): Coordonnée X du coin en bas à gauche du triangle en pixels
            y_base (float): Coordonnée Y du coin en bas à gauche du triangle en pixels
            hauteur (float): Hauteur du triangle en pixels
        """
        niveaux = int(hauteur / 16)
        for niveau in range(niveaux):
            # Largeur de chaque niveau augmente de 2 à partir de 1 tuile
            for decalage_x in range(1 + 2 * niveau):
                yield (x_base_gauche + decalage_x * 16, y_base - niveau * 16)

    def _creer_pont(self, x_base_gauche: float, y_base: float, largeur: float) -> Generator[tuple[float, float], Any, None]:
        """
        Crée une île en forme de pont horizontal avec quelques trous.

        Args:
            x_base_gauche (float): Coordonnée X du coin en bas à gauche du pont en pixels
            y_base (float): Coordonnée Y du coin en bas à gauche du pont en pixels
            largeur (float): Longueur totale du pont en pixels
        """
        largeur_tuiles = int(largeur / 16)
        for decalage_x in range(largeur_tuiles):
            yield (x_base_gauche + decalage_x * 16, y_base)
        for decalage_x in range(0, largeur_tuiles, 3):
            yield (x_base_gauche + decalage_x * 16, y_base - 16)

    def _creer_triangle_vertical(self, x_base_gauche: float, y_base: float, largeur: float, hauteur: float) -> Generator[tuple[float, float], Any, None]:
        """
        Crée un triangle vertical penché, avec une largeur qui diminue à chaque niveau.

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche du triangle en pixels.
            y_base: Coordonnée Y du coin en bas à gauche du triangle en pixels.
            largeur: Largeur initiale du triangle en pixels.
            hauteur: Hauteur du triangle en pixels.
        """
        niveaux = int(hauteur / 16)
        largeur_tuiles = int(largeur / 16)
        for niveau in range(niveaux):
            for decalage_x in range(largeur_tuiles - niveau):
                yield (x_base_gauche + decalage_x * 16 + niveau * 16, y_base - niveau * 16)

    def _creer_escalier(self, x_base_gauche: float, y_base: float, hauteur: float) -> Generator[tuple[float, float], Any, None]:
        """
        Crée un escalier pour relier des îles éloignées.

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche du premier bloc en pixels.
            y_base: Coordonnée Y du coin en bas à gauche du premier bloc en pixels.
            hauteur: Hauteur de l'escalier en pixels.
        """
        niveaux = int(hauteur / 16)
        x_courant: float = x_base_gauche
        y_courant: float = y_base
        for _ in range(niveaux):
            largeur_marche: int = random.randint(2, 4)
            for decalage_x in range(largeur_marche):
                yield (x_courant + decalage_x * 16, y_courant)
            x_courant += (largeur_marche + 1) * 16
            y_courant -= 16

    def _creer_rectangle(self, x_base_gauche: float, y_base: float, largeur: float, hauteur: float) -> Generator[tuple[float, float], Any, None]:
        """
        Crée une île rectangulaire ou carrée.

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche du rectangle en pixels.
            y_base: Coordonnée Y du coin en bas à gauche du rectangle en pixels.
            largeur: Largeur horizontale du rectangle en pixels.
            hauteur: Hauteur verticale du rectangle en pixels.
        """
        niveaux = int(hauteur / 16)
        largeur_tuiles = int(largeur / 16)
        for niveau in range(niveaux):
            for decalage_x in range(largeur_tuiles):
                yield (x_base_gauche + decalage_x * 16, y_base - niveau * 16)

    def _hauteur_libre(self, x_debut: float, largeur: float, carte: Carte) -> float:
        """Retourne la hauteur maximale où l'on peut placer une nouvelle île.

        Args:
            x_debut (float): Position X de début de la zone en pixels
            largeur (float): Largeur de la zone à vérifier en pixels

        Returns:
            float: Hauteur maximale pour éviter les superpositions en pixels
        """
        hauteur_max = HAUTEUR_MAX_GENERATION * 16
        # Vérifie les tuiles existantes dans la zone horizontale
        for decalage_x in range(0, int(largeur), 16):
            colonne_x: float = x_debut + decalage_x
            for hauteur in range(HAUTEUR_MIN_GENERATION * 16, int(hauteur_max) + 16, 16):
                if not carte.tuile_presente((colonne_x, hauteur)):
                    continue
                # Ajuste la base pour éviter la superposition
                if hauteur - 16 < hauteur_max:
                    hauteur_max = hauteur - 16
        return max(HAUTEUR_MIN_GENERATION * 16, hauteur_max)
    # endregion