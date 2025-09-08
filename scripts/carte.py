import random
from typing import Any, Sequence, Optional
import pygame
import json
import os
import tkinter as tk
from tkinter import filedialog
from scripts.tuile import Tuile, pos_en_str
from scripts.parametres import INDEXS_DE_DECALAGES, INDEXS_DE_DECALAGES_DIAGONAUX, INDEXS_DE_DECALAGES_DROITS
from scripts.type import TypeTuile

# * Constantes
TYPES_OBSTACLES: list[str] = ['herbe', 'pierre']
TYPES_AUTOTUILES = {"herbe", "pierre"}
CARTE_AUTOTUILES: dict[tuple[tuple[int, int], ...], int]= {
    tuple(sorted([(0 ,1), (1, 0)])): 0, # *En haut à gauche
    tuple(sorted([(-1, 0), (1, 0), (0, 1)])): 1, # *En haut au centre
    tuple(sorted([(-1, 0), (0, 1)])): 2, # *En haut à droite
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3, # *A droite
    tuple(sorted([(-1, 0), (0, -1)])): 4,# *En bas à droite
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,# *En bas au centre
    tuple(sorted([(0, -1), (1, 0)])): 6,# *En bas à gauche
    tuple(sorted([(0, -1), (0, 1), (1, 0)])): 7, # *A gauche
    tuple(sorted([(-1, 0), (0, -1), (1, 0), (0, 1)])): 8,# *Au milieu
    # ? Autres
    tuple(sorted([(1, 0)])): 0,
    tuple(sorted([(-1, 0), (1, 0)])): 1,
    tuple(sorted([(0, 1)])): 1,
    tuple(sorted([(1, 0)])): 1,
    tuple(sorted([(0, 1), (0, -1)])): 8,
    tuple(sorted([(-1, 0)])): 2,
    tuple(sorted([(0, -1)])): 5,
    tuple(sorted([(1, 0)])): 0,
}

class Carte:
    """Une classe représentant une carte"""

    def __init__(self, jeu:Any, taille: int = 16) -> None:
        self.jeu: Any = jeu
        self.taille_tuile: int = taille
        self.carte: dict[str, Tuile] = {}
        self.nom_fichier: Optional[str] = None

    def tuile_presente(self, pos: Sequence[int]) -> bool:
        return True if self.carte.get(pos_en_str(pos)) else False # pyright: ignore[reportArgumentType]

    def ajouter_tuile(self, x: int, y: int, type: TypeTuile) -> None:
        self.carte[f"{int(x)};{int(y)}"] = Tuile(type, (x, y), 0, self.jeu.rsc[type])

    def enlever_tuile(self, x: int, y: int) -> None:
        del self.carte[f"{x};{y}"]

    def remplir(self) -> None:
        """Cette fonction mets des tuiles dans les espaces vides et fermés de la carte"""
        for tuile in self.carte.copy().values():
            self.entourer(tuile)

    def entourer(self, tuile: Tuile) -> None:
        """Remplit les vides autour d'une tuile existante."""
        # Récupère les tuiles autour en droit et en diagonale
        voisins_droits: list[Tuile] = self._tuiles_autour(tuile, INDEXS_DE_DECALAGES_DROITS)
        voisins_diag: list[Tuile] = self._tuiles_autour(tuile, INDEXS_DE_DECALAGES_DIAGONAUX)

        nb_droits: int = len(voisins_droits)
        nb_diag: int = len(voisins_diag)

        # Cas où la tuile est isolée
        if nb_droits == 0 and nb_diag == 0:
            print(f"Une tuile {tuile} est au milieu de nulle part !!!")
            return

        # Supprime les tuiles diagonales seules si pas de voisins droits
        if nb_droits == 0 and nb_diag == 1:
            self.enlever_tuile(*voisins_diag[0].pos)
            return

        # Pour les autres configurations, on comble les vides selon les voisins
        if nb_droits == 0 and nb_diag in (2, 3, 4):
            # Décalage vertical pour 2 tuiles ou ajout de tuiles pour 3-4 tuiles
            if nb_diag == 2:
                tuile.pos = (tuile.pos[0], tuile.pos[1] + 1)
                self.ajouter_profondeur(tuile)
                for t in voisins_diag:
                    self.ajouter_profondeur(t)
            else:
                self._combler_espaces_vides(tuile, voisins_diag)
            return

        # Cas avec un voisin droit : on comble les diagonales si nécessaire
        if nb_droits == 1 and nb_diag in (2, 3, 4):
            self._combler_espaces_vides(tuile, voisins_diag)

    def _tuiles_autour(self, tuile: Tuile, decalages: list[tuple[int, int]] = INDEXS_DE_DECALAGES) -> list[Tuile]:
        """Renvoie la liste des tuiles présentes autour de la tuile selon les décalages donnés."""
        voisins: list[Tuile] = []
        for dx, dy in decalages:
            pos: tuple[int, int] = tuile.pos[0] + dx, tuile.pos[1] + dy
            if self.tuile_presente(pos):
                voisins.append(self.carte[pos_en_str(pos)])
        return voisins

    def _combler_espaces_vides(self, tuile: Tuile, voisins: list[Tuile]) -> None:
        """Ajoute des tuiles pour combler les espaces vides autour d'une tuile donnée."""
        pos_x: set[int] = {v.pos[0] for v in voisins}
        pos_y: set[int] = {v.pos[1] for v in voisins}
        for x in pos_x:
            self.ajouter_tuile(x, tuile.pos[1], tuile.type)
        for y in pos_y:
            self.ajouter_tuile(tuile.pos[0], y, tuile.type)

    def ajouter_profondeur(self, tuile: Tuile):
        for _ in range(1, 11): # 10-pos[1]
            self.ajouter_tuile(tuile.pos[0], tuile.pos[1]+_, tuile.type)

    #region Fonctions pour la génération en îles
    def _creer_triangle_inverse(self, x_base_gauche: int, y_base: int, largeur: int, hauteur: int, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de triangle inversé (pyramide renversée).

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche de la pyramide.
            y_base: Coordonnée Y du coin en bas à gauche de la pyramide.
            largeur: Largeur de la base du triangle.
            hauteur: Nombre de niveaux verticaux du triangle.
        """
        for niveau in range(hauteur):
            for decalage_x in range(largeur - 2 * niveau):
                self.ajouter_tuile(x_base_gauche + decalage_x + niveau, y_base - niveau, type_tuile)


    def _creer_triangle_normal(self, x_base_gauche: int, y_base: int, hauteur: int, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de triangle normal (pyramide classique).

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche du triangle.
            y_base: Coordonnée Y du coin en bas à gauche du triangle.
            hauteur: Nombre de niveaux verticaux.
        """
        for niveau in range(hauteur):
            # Largeur de chaque niveau augmente de 2 à partir de 1 tuile
            for decalage_x in range(1 + 2 * niveau):
                self.ajouter_tuile(x_base_gauche + decalage_x, y_base - niveau, type_tuile)


    def _creer_pont(self, x_base_gauche: int, y_base: int, largeur: int, type_tuile: TypeTuile) -> None:
        """
        Crée une île en forme de pont horizontal avec quelques trous.

        Args:
            x_base_gauche: Coordonnée X du coin en bas à gauche du pont.
            y_base: Coordonnée Y du coin en bas à gauche du pont.
            largeur: Longueur totale du pont.
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

    def _hauteur_libre(self, x_start, largeur) -> int:
        """
        Retourne la hauteur maximale où l'on peut placer une nouvelle île
        pour éviter qu'elle se retrouve sous une autre.
        """
        max_y = 10  # hauteur maximale pour la génération
        min_y = 3   # hauteur minimale
        # Vérifie les tuiles existantes dans la zone horizontale
        for dx in range(largeur):
            col_x = x_start + dx
            for y in range(min_y, max_y + 1):
                if not self.tuile_presente((col_x, y)):
                    continue
                # Ajuste la base pour éviter la superposition
                if y - 1 < max_y:
                    max_y = y - 1
        return max(min_y, max_y)

    #endregion

    def redessiner(self) -> None:
        """Redéssine la carte"""
        for _, tuile in self.carte.items():
            decalages_alentour = set()
            for dec in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                pos: tuple[int, int] = tuile.pos[0] + dec[0], tuile.pos[1] + dec[1]
                if self.tuile_presente(pos):
                    # if tuile['type'] == self.carte[loc]['type']:
                        decalages_alentour.add(dec)
            decalages_alentour = tuple(sorted(decalages_alentour))
            if (tuile.type in TYPES_AUTOTUILES) and (decalages_alentour in CARTE_AUTOTUILES):
                tuile.index = CARTE_AUTOTUILES[decalages_alentour]
            else:
                pass
                # print(f"[Carte.redessiner] Index adéquat introuvable pour la tuile {tuile}, {decalages_alentour=}")

    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None:
        for tuile in self.carte.values():
            tuile.afficher(surface, decalage)

    def enreg_carte(self) -> tuple[bool, str]:
        """
        Enregistre la carte actuelle dans un fichier JSON.
        Si nom_fichier est défini, sauvegarde dans ce fichier.
        Sinon, crée un nouveau fichier numéroté.
        
        Returns:
            tuple[bool, str]: (succès, message)
        """
        try:
            # Créer le répertoire s'il n'existe pas
            os.makedirs("rsc/cartes", exist_ok=True)
            
            # Déterminer le nom du fichier
            if self.nom_fichier is not None:
                chemin_fichier = f"rsc/cartes/{self.nom_fichier}"
            else:
                # Trouver le prochain numéro de fichier disponible
                i = 0
                while os.path.exists(f"rsc/cartes/{i}.json"):
                    i += 1
                chemin_fichier = f"rsc/cartes/{i}.json"
                self.nom_fichier = f"{i}.json"
            
            # Préparer les données à sauvegarder
            donnees_carte = {
                "taille_tuile": self.taille_tuile,
                "nom_fichier": self.nom_fichier,
                "carte": {pos: tuile.en_dict() for pos, tuile in self.carte.items()},
                "carte_deco": {
        "0;-100": {
            "type": "ennemi",
            "pos": [
                258,
                168
            ],
            "index": 0
        },
        "30;-100": {
            "type": "joueur",
            "pos": [
                140,
                163
            ],
            "index": 0
        }
    }
            }

            # Sauvegarder dans le fichier
            with open(chemin_fichier, 'w', encoding='utf-8') as f:
                json.dump(donnees_carte, f)
            
            return True, f"Carte '{self.nom_fichier}' sauvegardée ({len(self.carte)} tuiles)"
            
        except Exception as e:
            return False, f"Erreur lors de la sauvegarde : {str(e)}"

    def charger_carte(self) -> tuple[bool, str]:
        """
        Ouvre une boîte de dialogue pour charger un fichier de carte JSON.
        
        Returns:
            tuple[bool, str]: (succès, message)
        """
        try:
            # Créer une fenêtre Tkinter cachée
            root = tk.Tk()
            root.withdraw()
            
            # Ouvrir la boîte de dialogue de sélection de fichier
            chemin_fichier = filedialog.askopenfilename(
                title="Ouvrir une carte",
                initialdir="rsc/cartes",
                filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
            )
            
            # Fermer la fenêtre Tkinter
            root.destroy()
            
            if not chemin_fichier:
                return False, "Aucun fichier sélectionné"
            
            # Charger le fichier JSON
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                donnees = json.load(f)
            
            # Vider la carte actuelle
            self.carte.clear()
            
            # Charger les données
            self.taille_tuile = donnees.get("taille_tuile", 16)
            self.nom_fichier = donnees.get("nom_fichier")

            # Reconstruire les tuiles
            for pos_str, tuile_data in donnees.get("carte", {}).items():
                tuile = Tuile.from_dict(tuile_data, self.jeu.rsc[tuile_data["type"]])
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
