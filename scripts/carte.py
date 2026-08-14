"""Module définissant la classe Carte pour gérer la carte du jeu."""

import random
from typing import Any, Optional
import pygame
import json
import os
from tkinter import filedialog
from scripts.generation.type import BlocTuiles
from scripts.tuile import Decoration, Entite, Tuile, pos_en_str
from scripts.parametres import CARTE_REDESSIN, DECALAGE_HAUT, INDEXS_DECALAGES, INDEXS_DECALAGES_DIAGONAUX, INDEXS_DECALAGES_DROITS, INDEXS_DECALAGES_TUILES_EN_BAS, TYPES_REDESSIN
from scripts.parametres.type import TypeDecoration, TypeEntite, TypeTuile

# Constantes pour la génération
PROFONDEUR_MAX = 11
HAUTEUR_MAX_GENERATION = 10
HAUTEUR_MIN_GENERATION = 3


class Carte:
    """Représente une carte composée de tuiles dans le jeu.

    Cette classe gère la création, modification et affichage d'une carte procédurale
    composée de tuiles individuelles. Elle fournit des méthodes pour ajouter,
    supprimer et manipuler les tuiles selon les règles de génération.
    """

    def __init__(self, images_tuiles: dict[TypeTuile, list[pygame.Surface]], images_deco: dict[TypeDecoration, list[pygame.Surface]], images_entites: dict[TypeEntite, pygame.Surface]) -> None:
        """Initialise une nouvelle carte.
        """
        self.nom_fichier: Optional[str] = None

        self.carte_tuiles: dict[str, Tuile] = {}
        self.images_tuiles: dict[TypeTuile, list[pygame.Surface]] = images_tuiles
        self.tuiles_marchables: pygame.sprite.Group[Tuile] = pygame.sprite.Group()

        self.carte_deco: dict[str, Decoration] = {}
        self.images_deco: dict[TypeDecoration, list[pygame.Surface]] = images_deco
        self.tuiles_a_decorer: set[Tuile] = set()

        self.carte_entites: dict[TypeEntite, Entite | list[Entite]] = {}
        self.images_entites: dict[TypeEntite, pygame.Surface] = images_entites

    # region Opérations sur les tuiles
    def ajouter_tuile(self, pos_pixels: tuple[float, float], type_tuile: TypeTuile) -> None:
        """Ajoute une nouvelle tuile à la position spécifiée.

        Args:
            pos_pixels (tuple[float, float]): Position en pixels absolus
            type_tuile (TypeTuile): Type de la tuile à ajouter
        """
        cle_position: str = pos_en_str(pos_pixels)
        tuile = Tuile(type_tuile, 0, pos_pixels, self.images_tuiles[type_tuile][0])
        self.carte_tuiles[cle_position] = tuile

    def enlever_tuile(self, pos_pixels: tuple[float, float]) -> None:
        """Supprime la tuile à la position spécifiée.

        Args:
            pos_pixels (tuple[float, float]): Position en pixels
        """
        cle: str = pos_en_str(pos_pixels)
        del self.carte_tuiles[cle]
    # endregion

    # region Informations sur les tuiles
    def tuile_presente(self, pos_pixels: tuple[float, float]) -> bool:
        """Vérifie si une tuile existe à la position donnée.

        Args:
            pos_pixels (tuple[float, float]): Coordonnées (x, y) en pixels à vérifier

        Returns:
            bool: True si une tuile existe à cette position
        """
        return pos_en_str(pos_pixels) in self.carte_tuiles

    def _tuiles_autour(self, tuile: Tuile, decalages: list[tuple[int, int]] = INDEXS_DECALAGES) -> list[Tuile]:
        """Renvoie la liste des tuiles présentes autour de la tuile selon les décalages donnés.

        Args:
            tuile (Tuile): Tuile centrale
            decalages (list[tuple[int, int]]): Liste des décalages en tuiles

        Returns:
            list[Tuile]: Liste des tuiles voisines trouvées
        """
        voisins: list[Tuile] = []
        for decalage_x, decalage_y in decalages:
            pos_pixels = (tuile.rect.x + decalage_x * 16, tuile.rect.y + decalage_y * 16)
            if self.tuile_presente(pos_pixels):
                voisins.append(self.carte_tuiles[pos_en_str(pos_pixels)])
        return voisins

    # Organisation des tuiles
    def definir_groupes_tuiles(self) -> None:
        self.tuiles_marchables = pygame.sprite.Group(self._tuiles_en_haut())
        for tuile in self.tuiles_marchables:
            image = tuile.image.copy()
            image.fill("yellow")
            tuile.image = image

    def _tuiles_en_haut(self) -> list[Tuile]:
        """Renvoie la liste des tuiles sur lesquelles le joueur va pouvoir marcher"""
        marchables: list[Tuile] = []
        for tuile in self.carte_tuiles.values():
            voisins = self._tuiles_autour(tuile, INDEXS_DECALAGES)
            if len(voisins) > 5:
                continue
            if self._tuiles_autour(tuile, INDEXS_DECALAGES_TUILES_EN_BAS):
                continue
            marchables.append(tuile)
        return marchables

    def _decouper_tuiles_en_blocs(self) -> list[BlocTuiles]:
        """Découpe les tuiles marchables en blocs contigus à la même hauteur.

        Returns:
            list[Bloc]: Liste des blocs, chaque bloc regroupant des tuiles à la
            même hauteur et horizontalement contiguës.
        """
        tuiles_par_hauteur: dict[float, list[Tuile]] = {}
        for tuile in self.tuiles_marchables:
            tuiles_par_hauteur.setdefault(tuile.rect.y, []).append(tuile)

        blocs: list[BlocTuiles] = []
        for tuiles in tuiles_par_hauteur.values():
            tuiles_triees: list[Tuile] = sorted(tuiles, key=lambda tuile: tuile.rect.x)
            bloc_courant: list[Tuile] = [tuiles_triees[0]]
            for tuile in tuiles_triees[1:]:
                if tuile.rect.x - bloc_courant[-1].rect.x > 16:
                    blocs.append(BlocTuiles.depuis_tuiles(bloc_courant))
                    bloc_courant = [tuile]
                else:
                    bloc_courant.append(tuile)
            blocs.append(BlocTuiles.depuis_tuiles(bloc_courant))
        return blocs

    def _extraire_blocs_tuiles_marchables(self, nb_tuiles_minimal: int) -> list[BlocTuiles]:
        blocs: list[BlocTuiles] = self._decouper_tuiles_en_blocs()

        for bloc in blocs.copy():
            if bloc.nb_tuiles < nb_tuiles_minimal:
                blocs.remove(bloc)

        return blocs

    # endregion

    # region Gestion des décorations
    def ajouter_deco(self, rect: pygame.FRect, type_tuile: TypeDecoration, index: Optional[int]) -> None:
        """Ajoute une nouvelle décoration à la position spécifiée.

        Args:
            rect (pygame.FRect): Rectangle de la décoration
            type_tuile (TypeDecoration): Type de la décoration à ajouter
            index (Optional[int]): L'index de l'image de décoration à utiliser. Si None, un index aléatoire est choisi.
        """
        index = index or random.choice(range(len(self.images_deco[type_tuile])))
        deco = Decoration(type_tuile, index, rect.topleft, self.images_deco[type_tuile][index])
        self.carte_deco[pos_en_str(rect.topleft)] = deco

    def enlever_deco(self, x: int, y: int) -> None:
        """Supprime la décoration à la position spécifiée.

        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
        """
        del self.carte_deco[pos_en_str((x, y))]

    def generer_deco(self) -> None:
        """Génère des décorations aléatoires sur les tuiles existantes."""
        for tuile in self.tuiles_marchables:
            if random.random() < 0.5:
                type_deco: TypeDecoration = random.choice(list(self.images_deco.keys()))
                index = random.choice(range(len(self.images_deco[type_deco])))
                image = self.images_deco[type_deco][index].copy()
                rect = image.get_frect(midbottom = tuile.rect.midtop)
                self.ajouter_deco(rect, type_deco, index)
    # endregion

    # region Gestion des entités
    def generer_entite(self, type_entite: TypeEntite) -> None:
        match type_entite:
            case "joueur":
                self.ajouter_joueur()
            case "ennemi":
                self.ajouter_ennemis()
            case _:
                raise ValueError(f"Le type d'entité {type_entite} n'est pas pris en charge")

    def ajouter_ennemis(self) -> None:
        self.carte_entites["ennemi"] = []
        for bloc in self._extraire_blocs_tuiles_marchables(3):
            tuile_choisie: Tuile = min(bloc.tuiles, key=lambda tuile: abs(tuile.rect.x - bloc.milieu))
            for i in range(random.randint(0, bloc.nb_tuiles)):
                self.carte_entites["ennemi"].append(Entite("ennemi", self.images_entites["ennemi"].get_frect(left=tuile_choisie.rect.left, bottom=tuile_choisie.rect.top - 16*5).topleft, self.images_entites["ennemi"])) # pyright: ignore[reportAttributeAccessIssue]

    def ajouter_joueur(self) -> None:
        tuile_choisie: Tuile = self.tuiles_marchables.sprites()[0]

        resultat_tuile_en_haut: list[Tuile] = self._tuiles_autour(tuile_choisie, [DECALAGE_HAUT])
        while len(resultat_tuile_en_haut) != 0:
            tuile_choisie = resultat_tuile_en_haut[0]
            resultat_tuile_en_haut = self._tuiles_autour(tuile_choisie, [DECALAGE_HAUT])

        image_joueur = self.images_entites["joueur"]
        rect_joueur = image_joueur.get_frect()
        rect_joueur.bottomleft = tuile_choisie.rect.topleft
        rect_joueur.bottom -= 16*5
        joueur = Entite("joueur", rect_joueur.topleft, image_joueur)
        self.carte_entites["joueur"] = joueur
    # endregion

    # region Remplissage de la carte
    def remplir(self) -> None:
        """Remplit les espaces vides et fermés de la carte avec des tuiles."""
        for tuile in self.carte_tuiles.copy().values():
            self.entourer(tuile)

    def entourer(self, tuile: Tuile) -> None:
        """Remplit les vides autour d'une tuile existante selon les règles de génération.

        Args:
            tuile (Tuile): Tuile autour de laquelle remplir les vides
        """
        # Récupère les tuiles autour en droit et en diagonale
        voisins_droits: list[Tuile] = self._tuiles_autour(tuile, INDEXS_DECALAGES_DROITS)
        voisins_diagonaux: list[Tuile] = self._tuiles_autour(tuile, INDEXS_DECALAGES_DIAGONAUX)

        nombre_voisins_droits: int = len(voisins_droits)
        nombre_voisins_diagonaux: int = len(voisins_diagonaux)

        # Cas où la tuile est isolée
        if nombre_voisins_droits == 0 and nombre_voisins_diagonaux == 0:
            self.enlever_tuile((tuile.rect.x, tuile.rect.y))
            return

        # Supprime les tuiles diagonales seules si pas de voisins droits
        if nombre_voisins_droits == 0 and nombre_voisins_diagonaux == 1:
            self.enlever_tuile((voisins_diagonaux[0].rect.x, voisins_diagonaux[0].rect.y))
            return

        # Pour les autres configurations, on comble les vides selon les voisins
        if nombre_voisins_droits == 0 and nombre_voisins_diagonaux in (2, 3, 4):
            # Décalage vertical pour 2 tuiles ou ajout de tuiles pour 3-4 tuiles
            if nombre_voisins_diagonaux == 2:
                tuile.rect.y += 16
                for voisin in (*voisins_diagonaux, tuile):
                    self.ajouter_profondeur(voisin)
            else:
                self._combler_espaces_vides(tuile, voisins_diagonaux)
            return

        # Cas avec un voisin droit : on comble les diagonales si nécessaire
        if nombre_voisins_droits == 1 and nombre_voisins_diagonaux in (2, 3, 4):
            self._combler_espaces_vides(tuile, voisins_diagonaux)

    def _combler_espaces_vides(self, tuile: Tuile, voisins: list[Tuile]) -> None:
        """Ajoute des tuiles pour combler les espaces vides autour d'une tuile donnée.

        Args:
            tuile (Tuile): Tuile centrale
            voisins (list[Tuile]): Liste des tuiles voisines
        """
        positions_x: set[float] = {voisin.rect.x for voisin in voisins}
        positions_y: set[float] = {voisin.rect.y for voisin in voisins}
        for x in positions_x:
            self.ajouter_tuile((x, tuile.rect.y), tuile.type)
        for y in positions_y:
            self.ajouter_tuile((tuile.rect.x, y), tuile.type)

    def ajouter_profondeur(self, tuile: Tuile) -> None:
        """Ajoute des tuiles en profondeur sous la tuile donnée.

        Args:
            tuile (Tuile): Tuile de référence
        """
        for profondeur in range(1, PROFONDEUR_MAX):
            self.ajouter_tuile((tuile.rect.x, tuile.rect.y + profondeur * 16), tuile.type)
    # endregion

    #region Génération des îles
    def _creer_triangle_inverse(self, x_base_gauche: float, y_base: float, largeur: float, hauteur: float, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de triangle inversé (pyramide renversée).

        Args:
            x_base_gauche (float): Coordonnée X du coin en bas à gauche de la pyramide en pixels
            y_base (float): Coordonnée Y du coin en bas à gauche de la pyramide en pixels
            largeur (float): Largeur de la base du triangle en pixels
            hauteur (float): Hauteur du triangle en pixels
            type_tuile (TypeTuile): Type de tuile à utiliser
        """
        niveaux = int(hauteur / 16)
        largeur_tuiles = int(largeur / 16)
        for niveau in range(niveaux):
            for decalage_x in range(largeur_tuiles - 2 * niveau):
                self.ajouter_tuile((x_base_gauche + decalage_x * 16 + niveau * 16, y_base - niveau * 16), type_tuile)

    def _creer_triangle_normal(self, x_base_gauche: float, y_base: float, hauteur: float, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de triangle normal (pyramide classique).

        Args:
            x_base_gauche (float): Coordonnée X du coin en bas à gauche du triangle en pixels
            y_base (float): Coordonnée Y du coin en bas à gauche du triangle en pixels
            hauteur (float): Hauteur du triangle en pixels
            type_tuile (TypeTuile): Type de tuile à utiliser
        """
        niveaux = int(hauteur / 16)
        for niveau in range(niveaux):
            # Largeur de chaque niveau augmente de 2 à partir de 1 tuile
            for decalage_x in range(1 + 2 * niveau):
                self.ajouter_tuile((x_base_gauche + decalage_x * 16, y_base - niveau * 16), type_tuile)

    def _creer_pont(self, x_base_gauche: float, y_base: float, largeur: float, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de pont horizontal avec quelques trous.

        Args:
            x_base_gauche (float): Coordonnée X du coin en bas à gauche du pont en pixels
            y_base (float): Coordonnée Y du coin en bas à gauche du pont en pixels
            largeur (float): Longueur totale du pont en pixels
            type_tuile (TypeTuile): Type de tuile à utiliser
        """
        largeur_tuiles = int(largeur / 16)
        for decalage_x in range(largeur_tuiles):
            self.ajouter_tuile((x_base_gauche + decalage_x * 16, y_base), type_tuile)
        for decalage_x in range(0, largeur_tuiles, 3):
            self.ajouter_tuile((x_base_gauche + decalage_x * 16, y_base - 16), type_tuile)

    def _creer_triangle_vertical(self, x_base_gauche: float, y_base: float, largeur: float, hauteur: float, type_tuile: TypeTuile) -> None:
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
                self.ajouter_tuile((x_base_gauche + decalage_x * 16 + niveau * 16, y_base - niveau * 16), type_tuile)

    def _creer_escalier(self, x_base_gauche: float, y_base: float, hauteur: float, type_tuile: TypeTuile) -> None:
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
                self.ajouter_tuile((x_courant + decalage_x * 16, y_courant), type_tuile)
            x_courant += (largeur_marche + 1) * 16
            y_courant -= 16

    def _creer_rectangle(self, x_base_gauche: float, y_base: float, largeur: float, hauteur: float, type_tuile: TypeTuile) -> None:
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
                self.ajouter_tuile((x_base_gauche + decalage_x * 16, y_base - niveau * 16), type_tuile)

    def _hauteur_libre(self, x_debut: float, largeur: float) -> float:
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
                if not self.tuile_presente((colonne_x, hauteur)):
                    continue
                # Ajuste la base pour éviter la superposition
                if hauteur - 16 < hauteur_max:
                    hauteur_max = hauteur - 16
        return max(HAUTEUR_MIN_GENERATION * 16, hauteur_max)

    # endregion

    # region Gestion du rendu
    def redessiner(self) -> None:
        """Met à jour les indices des sprites de toutes les tuiles selon leur voisinage."""
        for tuile in self.carte_tuiles.values():
            decalages_voisins: set[tuple[int, int]] = set()
            decalages_directions: list[tuple[int, int]] = [
                (-1, 0),  # Gauche
                (0, -1),  # Haut
                (1, 0),   # Droite
                (0, 1)    # Bas
            ]
            for decalage in decalages_directions:
                pos_pixels = (tuile.rect.x + decalage[0] * 16, tuile.rect.y + decalage[1] * 16)
                if self.tuile_presente(pos_pixels):
                    voisin: Tuile = self.carte_tuiles[pos_en_str(pos_pixels)]
                    if tuile.type == voisin.type:
                        decalages_voisins.add(decalage)

            configuration_voisins: tuple[tuple[int, int], ...] = tuple(sorted(decalages_voisins))
            if (tuile.type in TYPES_REDESSIN) and (configuration_voisins in CARTE_REDESSIN):
                tuile.index = CARTE_REDESSIN[configuration_voisins]

            tuile.image = self.images_tuiles[tuile.type][tuile.index]
    # endregion

    # region Sauvegarde et chargement
    def enregistrer_carte(self) -> tuple[bool, str]:
        """Enregistre la carte actuelle dans un fichier JSON.

        Returns:
            Tuple (succès, message) indiquant le résultat de l'opération
        """
        try:
            # Créer le répertoire s'il n'existe pas
            os.makedirs("rsc/cartes", exist_ok=True)

            # Déterminer le nom du fichier
            if self.nom_fichier is not None:
                chemin_fichier = f"rsc/cartes/{self.nom_fichier}"
            else:
                # Trouver le prochain numéro de fichier disponible
                numero_fichier = 0
                while os.path.exists(f"rsc/cartes/{numero_fichier}.json"):
                    numero_fichier += 1
                chemin_fichier: str = f"rsc/cartes/{numero_fichier}.json"
                self.nom_fichier = f"{numero_fichier}.json"

            # Préparer les données à sauvegarder
            donnees_carte: dict[str, str | dict[str, dict[str, Any]]] = {
                # "nom_fichier": self.nom_fichier,
                "tuiles": {position: tuile.en_dict() for position, tuile in self.carte_tuiles.items()},
                "deco": {position: deco.en_dict() for position, deco in self.carte_deco.items()},
            }

            # Sauvegarder dans le fichier
            with open(chemin_fichier, 'w', encoding='utf-8') as fichier:
                json.dump(donnees_carte, fichier)

            return True, f"Carte '{self.nom_fichier}' sauvegardée ({len(self.carte_tuiles)} tuiles)"

        except Exception as erreur:
            return False, f"Erreur lors de la sauvegarde : {str(erreur)}"

    def charger_carte(self) -> tuple[bool, str]:
        """
        Ouvre une boîte de dialogue pour charger un fichier de carte JSON.

        Returns:
            tuple[bool, str]: (succès, message)
        """
        try:
            # Créer le répertoire s'il n'existe pas
            os.makedirs("rsc/cartes", exist_ok=True)

            # Ouvrir la boîte de dialogue de sélection de fichier
            chemin_fichier: str = filedialog.askopenfilename(
                title="Ouvrir une carte",
                initialdir="rsc/cartes",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )

            if not chemin_fichier:
                return False, "Aucun fichier sélectionné"

            # Charger le fichier JSON
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                donnees: dict[str, Any] = json.load(f)

            # Vider la carte actuelle
            self.carte_tuiles.clear()

            # Charger les données du fichier
            self.nom_fichier = os.path.basename(chemin_fichier)

            # Reconstruire les tuiles à partir de ces données
            for pos_str, infos_tuile in donnees["tuiles"].items():
                tuile: Tuile = Tuile.de_dict(infos_tuile, self.images_tuiles[infos_tuile["type"]][infos_tuile["index"]])
                self.carte_tuiles[pos_str] = tuile

            # Reconstruire les décorations à partir de ces données
            for pos_str, infos_deco in donnees.get("deco", {}).items():
                deco = Decoration(infos_deco["type"], infos_deco["index"], infos_deco["pos"], self.images_deco[infos_deco["type"]][infos_deco["index"]])
                self.carte_deco[pos_str] = deco

            # Si nom_fichier n'est pas défini dans le fichier, utiliser le basename
            if self.nom_fichier is None:
                self.nom_fichier = os.path.basename(chemin_fichier)

            return True, f"Carte '{self.nom_fichier}' chargée ({len(self.carte_tuiles)} tuiles)"

        except Exception as e:
            return False, f"Erreur lors du chargement : {str(e)}"

    def nouvelle_carte(self) -> tuple[bool, str]:
        """
        Crée une nouvelle carte vide.

        Returns:
            tuple[bool, str]: (succès, message)
        """
        try:
            # Vider la carte actuelle
            self.carte_tuiles.clear()
            self.carte_deco.clear()

            # Réinitialiser le nom de fichier
            self.nom_fichier = None

            return True, "Nouvelle carte créée (0 tuiles)"

        except Exception as e:
            return False, f"Erreur lors de la création d'une nouvelle carte : {str(e)}"

    def effacer_tuiles(self) -> None:
        """Efface toutes les tuiles de la carte."""
        self.__init__(self.images_tuiles, self.images_deco, self.images_entites)
    # endregion
