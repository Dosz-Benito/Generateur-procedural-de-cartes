"""Module définissant la classe Carte pour gérer la carte du jeu."""

import random
from typing import Any, Iterable, Sequence, Optional
import pygame
import json
import os
from tkinter import filedialog
from scripts.tuile import Tuile, pos_en_str
from scripts.parametres import CARTE_REDESSIN, INDEXS_DECALAGES, INDEXS_DECALAGES_DIAGONAUX, INDEXS_DECALAGES_DROITS, TYPES_REDESSIN, TYPES_TUILES
from scripts.type import TypeTuile

TAILLE_TUILE_DEFAUT = 16

# Constantes pour la génération
PROFONDEUR_MAX_DEFAUT = 11
HAUTEUR_MAX_GENERATION = 10
HAUTEUR_MIN_GENERATION = 3


class Carte:
    """Représente une carte composée de tuiles dans le jeu.

    Cette classe gère la création, modification et affichage d'une carte procédurale
    composée de tuiles individuelles. Elle fournit des méthodes pour ajouter,
    supprimer et manipuler les tuiles selon les règles de génération.
    """

    def __init__(self, editeur: Any, taille: int = TAILLE_TUILE_DEFAUT) -> None:
        """Initialise une nouvelle carte.

        Args:
            editeur (Any): Référence vers l'éditeur principal
            taille (int): Taille en pixels d'une tuile
        """
        self.taille_tuile: int = taille
        self.carte: dict[str, Tuile] = {}
        self.nom_fichier: Optional[str] = None
        self.editeur = editeur
        images_tuiles: list[list[pygame.Surface]] = [
            [editeur.ressources[t][i] for i in range(len(editeur.ressources[t]))]
            for t in TYPES_TUILES
        ]
        self.images_tuiles: list[pygame.Surface] = [
            img for sublist in images_tuiles for img in sublist
        ]

    def tuile_presente(self, position: Sequence[int]) -> bool:
        """Vérifie si une tuile existe à la position donnée.

        Args:
            position (Sequence[int]): Coordonnées (x, y) à vérifier

        Returns:
            bool: True si une tuile existe à cette position
        """
        return pos_en_str(position) in self.carte

    def ajouter_tuile(self, x: int, y: int, type_tuile: TypeTuile) -> None:
        """Ajoute une nouvelle tuile à la position spécifiée.

        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
            type_tuile (TypeTuile): Type de la tuile à ajouter
        """
        cle_position = f"{int(x)};{int(y)}"
        self.carte[cle_position] = Tuile(
            type_tuile,
            (x, y),
            0,
            self.editeur.ressources[type_tuile][0]
        )

    def enlever_tuile(self, x: int, y: int) -> None:
        """Supprime la tuile à la position spécifiée.

        Args:
            x (int): Coordonnée X
            y (int): Coordonnée Y
        """
        cle_position = f"{x};{y}"
        del self.carte[cle_position]

    def remplir(self) -> None:
        """Remplit les espaces vides et fermés de la carte avec des tuiles."""
        for tuile in self.carte.copy().values():
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
            print(f"Une tuile {tuile} est au milieu de nulle part !!!")
            return

        # Supprime les tuiles diagonales seules si pas de voisins droits
        if nombre_voisins_droits == 0 and nombre_voisins_diagonaux == 1:
            self.enlever_tuile(*voisins_diagonaux[0].pos)
            return

        # Pour les autres configurations, on comble les vides selon les voisins
        if nombre_voisins_droits == 0 and nombre_voisins_diagonaux in (2, 3, 4):
            # Décalage vertical pour 2 tuiles ou ajout de tuiles pour 3-4 tuiles
            if nombre_voisins_diagonaux == 2:
                tuile.pos = (tuile.pos[0], tuile.pos[1] + 1)
                self.ajouter_profondeur(tuile)
                for voisin in voisins_diagonaux:
                    self.ajouter_profondeur(voisin)
            else:
                self._combler_espaces_vides(tuile, voisins_diagonaux)
            return

        # Cas avec un voisin droit : on comble les diagonales si nécessaire
        if nombre_voisins_droits == 1 and nombre_voisins_diagonaux in (2, 3, 4):
            self._combler_espaces_vides(tuile, voisins_diagonaux)

    def _tuiles_autour(self, tuile: Tuile, decalages: list[tuple[int, int]] = INDEXS_DECALAGES) -> list[Tuile]:
        """Renvoie la liste des tuiles présentes autour de la tuile selon les décalages donnés.

        Args:
            tuile (Tuile): Tuile centrale
            decalages (list[tuple[int, int]]): Liste des décalages à vérifier

        Returns:
            list[Tuile]: Liste des tuiles voisines trouvées
        """
        voisins: list[Tuile] = []
        for decalage_x, decalage_y in decalages:
            position = (tuile.pos[0] + decalage_x, tuile.pos[1] + decalage_y)
            if self.tuile_presente(position):
                voisins.append(self.carte[pos_en_str(position)])
        return voisins

    def _combler_espaces_vides(self, tuile: Tuile, voisins: list[Tuile]) -> None:
        """Ajoute des tuiles pour combler les espaces vides autour d'une tuile donnée.

        Args:
            tuile (Tuile): Tuile centrale
            voisins (list[Tuile]): Liste des tuiles voisines
        """
        positions_x: set[int] = {voisin.pos[0] for voisin in voisins}
        positions_y: set[int] = {voisin.pos[1] for voisin in voisins}
        for x in positions_x:
            self.ajouter_tuile(x, tuile.pos[1], tuile.type)
        for y in positions_y:
            self.ajouter_tuile(tuile.pos[0], y, tuile.type)

    def ajouter_profondeur(self, tuile: Tuile) -> None:
        """Ajoute des tuiles en profondeur sous la tuile donnée.

        Args:
            tuile (Tuile): Tuile de référence
        """
        for profondeur in range(1, PROFONDEUR_MAX_DEFAUT):
            self.ajouter_tuile(tuile.pos[0], tuile.pos[1] + profondeur, tuile.type)

    #region Fonctions pour la génération en îles
    def _creer_triangle_inverse(self, x_base_gauche: int, y_base: int, largeur: int, hauteur: int, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de triangle inversé (pyramide renversée).

        Args:
            x_base_gauche (int): Coordonnée X du coin en bas à gauche de la pyramide
            y_base (int): Coordonnée Y du coin en bas à gauche de la pyramide
            largeur (int): Largeur de la base du triangle
            hauteur (int): Nombre de niveaux verticaux du triangle
            type_tuile (TypeTuile): Type de tuile à utiliser
        """
        for niveau in range(hauteur):
            for decalage_x in range(largeur - 2 * niveau):
                self.ajouter_tuile(x_base_gauche + decalage_x + niveau, y_base - niveau, type_tuile)


    def _creer_triangle_normal(self, x_base_gauche: int, y_base: int, hauteur: int, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de triangle normal (pyramide classique).

        Args:
            x_base_gauche (int): Coordonnée X du coin en bas à gauche du triangle
            y_base (int): Coordonnée Y du coin en bas à gauche du triangle
            hauteur (int): Nombre de niveaux verticaux
            type_tuile (TypeTuile): Type de tuile à utiliser
        """
        for niveau in range(hauteur):
            # Largeur de chaque niveau augmente de 2 à partir de 1 tuile
            for decalage_x in range(1 + 2 * niveau):
                self.ajouter_tuile(x_base_gauche + decalage_x, y_base - niveau, type_tuile)


    def _creer_pont(self, x_base_gauche: int, y_base: int, largeur: int, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de pont horizontal avec quelques trous.

        Args:
            x_base_gauche (int): Coordonnée X du coin en bas à gauche du pont
            y_base (int): Coordonnée Y du coin en bas à gauche du pont
            largeur (int): Longueur totale du pont
            type_tuile (TypeTuile): Type de tuile à utiliser
        """
        for decalage_x in range(largeur):
            self.ajouter_tuile(x_base_gauche + decalage_x, y_base, type_tuile)
        for decalage_x in range(0, largeur, 3):
            self.ajouter_tuile(x_base_gauche + decalage_x, y_base - 1, type_tuile)


    def _creer_triangle_vertical(self, x_base_gauche: int, y_base: int, largeur: int, hauteur: int, type_tuile: TypeTuile) -> None:
        """
        Crée un triangle vertical penché, avec une largeur qui diminue à chaque niveau.

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche du triangle.
            y_base: Coordonnée Y du coin en bas à gauche du triangle.
            largeur: Largeur initiale du triangle.
            hauteur: Nombre de niveaux verticaux.
        """
        for niveau in range(hauteur):
            for decalage_x in range(largeur - niveau):
                self.ajouter_tuile(x_base_gauche + decalage_x + niveau, y_base - niveau, type_tuile)


    def _creer_escalier(self, x_base_gauche: int, y_base: int, hauteur: int, type_tuile: TypeTuile) -> None:
        """
        Crée un escalier pour relier des îles éloignées.

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche du premier bloc.
            y_base: Coordonnée Y du coin en bas à gauche du premier bloc.
            hauteur: Nombre de marches de l'escalier.
        """
        x_courant = x_base_gauche
        y_courant = y_base
        for _ in range(hauteur):
            largeur_marche = random.randint(2, 4)
            for decalage_x in range(largeur_marche):
                self.ajouter_tuile(x_courant + decalage_x, y_courant, type_tuile)
            x_courant += largeur_marche + 1
            y_courant -= 1


    def _creer_rectangle(self, x_base_gauche: int, y_base: int, largeur: int, hauteur: int, type_tuile: TypeTuile) -> None:
        """
        Crée une île rectangulaire ou carrée.

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche du rectangle.
            y_base: Coordonnée Y du coin en bas à gauche du rectangle.
            largeur: Largeur horizontale du rectangle.
            hauteur: Hauteur verticale du rectangle.
        """
        for niveau in range(hauteur):
            for decalage_x in range(largeur):
                self.ajouter_tuile(x_base_gauche + decalage_x, y_base - niveau, type_tuile)

    def _hauteur_libre(self, x_debut: int, largeur: int) -> int:
        """Retourne la hauteur maximale où l'on peut placer une nouvelle île.

        Args:
            x_debut (int): Position X de début de la zone
            largeur (int): Largeur de la zone à vérifier

        Returns:
            int: Hauteur maximale pour éviter les superpositions
        """
        hauteur_max = HAUTEUR_MAX_GENERATION
        # Vérifie les tuiles existantes dans la zone horizontale
        for decalage_x in range(largeur):
            colonne_x = x_debut + decalage_x
            for hauteur in range(HAUTEUR_MIN_GENERATION, hauteur_max + 1):
                if not self.tuile_presente((colonne_x, hauteur)):
                    continue
                # Ajuste la base pour éviter la superposition
                if hauteur - 1 < hauteur_max:
                    hauteur_max = hauteur - 1
        return max(HAUTEUR_MIN_GENERATION, hauteur_max)

    #endregion

    def redessiner(self) -> None:
        """Met à jour les indices des sprites de toutes les tuiles selon leur voisinage."""
        for tuile in self.carte.values():
            decalages_voisins: set[tuple[int, int]] = set()
            decalages_directions = [
                (-1, 0),  # Gauche
                (0, -1),  # Haut
                (1, 0),   # Droite
                (0, 1)    # Bas
            ]
            for decalage in decalages_directions:
                position = (tuile.pos[0] + decalage[0], tuile.pos[1] + decalage[1])
                if self.tuile_presente(position):
                    voisin = self.carte[pos_en_str(position)]
                    if tuile.type == voisin.type:
                        decalages_voisins.add(decalage)

            configuration_voisins = tuple(sorted(decalages_voisins))
            if (tuile.type in TYPES_REDESSIN) and (configuration_voisins in CARTE_REDESSIN):
                tuile.index = CARTE_REDESSIN[configuration_voisins]

            tuile.image = self.editeur.ressources[tuile.type][tuile.index]

    def afficher(self, surface: pygame.Surface, decalage_camera: pygame.Vector2) -> None:
        """Affiche toutes les tuiles de la carte sur la surface donnée.

        Args:
            surface (pygame.Surface): Surface Pygame où afficher les tuiles
            decalage_camera (pygame.Vector2): Décalage de la caméra (x, y)
        """
        for tuile in self.carte.values():
            tuile.afficher(surface, decalage_camera)

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
                chemin_fichier = f"rsc/cartes/{numero_fichier}.json"
                self.nom_fichier = f"{numero_fichier}.json"

            # Préparer les données à sauvegarder
            donnees_carte = {
                "taille_tuile": self.taille_tuile,
                "nom_fichier": self.nom_fichier,
                "carte": {position: tuile.en_dict() for position, tuile in self.carte.items()},
            }

            # Sauvegarder dans le fichier
            with open(chemin_fichier, 'w', encoding='utf-8') as fichier:
                json.dump(donnees_carte, fichier)

            return True, f"Carte '{self.nom_fichier}' sauvegardée ({len(self.carte)} tuiles)"

        except Exception as erreur:
            return False, f"Erreur lors de la sauvegarde : {str(erreur)}"

    def charger_carte(self) -> tuple[bool, str]:
        """
        Ouvre une boîte de dialogue pour charger un fichier de carte JSON.

        Returns:
            tuple[bool, str]: (succès, message)
        """
        try:
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
            self.carte.clear()

            # Charger les données
            self.taille_tuile = donnees.get("taille_tuile", 16)
            self.nom_fichier = donnees.get("nom_fichier")

            # Reconstruire les tuiles
            for pos_str, infos_tuile in donnees.get("carte", {}).items():
                tuile: Tuile = Tuile.de_dict(infos_tuile, self.images_tuiles[infos_tuile["index"]])
                self.carte[pos_str] = tuile

            # Si nom_fichier n'est pas défini dans le fichier, utiliser le basename
            if self.nom_fichier is None:
                self.nom_fichier = os.path.basename(chemin_fichier)

            return True, f"Carte '{self.nom_fichier}' chargée ({len(self.carte)} tuiles)"

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
            self.carte.clear()

            # Réinitialiser le nom de fichier
            self.nom_fichier = None

            return True, "Nouvelle carte créée (0 tuiles)"

        except Exception as e:
            return False, f"Erreur lors de la création d'une nouvelle carte : {str(e)}"

