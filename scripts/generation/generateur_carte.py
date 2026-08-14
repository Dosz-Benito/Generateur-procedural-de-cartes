import random
from typing import Literal
from warnings import deprecated
import pygame
from scripts.carte import Carte
from scripts.parametres import DECALAGE_BAS, DECALAGE_DROITE, DECALAGE_GAUCHE, DECALAGE_HAUT, TypeTuile
from scripts.parametres.type import TypeDecoration, TypeEntite
from scripts.tuile import Tuile, Entite


class GenerateurCarte:
    def __init__(self, nombre_tuiles_max_horizontal: int, longueur_tuile: int = 16, largeur_tuile: int = 16, ) -> None:
        self.nombre_tuiles: int = nombre_tuiles_max_horizontal
        self.longueur_tuile: int = longueur_tuile
        self.largeur_tuile: int = largeur_tuile

        # ! A supprimer avec la fonction self.generation_procedurale_bloc
        self.probabilite_monter: float = 0.0
        self.probabilite_gauche: float = 0.0

    def generer(self, type_terrain: Literal["Ile", "Bloc"], images_tuiles: dict[TypeTuile, list[pygame.Surface]], images_deco: dict[TypeDecoration, list[pygame.Surface]], images_entites: dict[TypeEntite, pygame.Surface]) -> Carte:
        """Génère la carte selon le type de génération demandé.

        Args:
            type_terrain (Literal["Ile", "Bloc"]): Type de génération à utiliser pour le terrain.
        """
        carte = Carte(images_tuiles, images_deco, images_entites) # pyright: ignore[reportArgumentType]
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
            hauteur_base: float = carte._hauteur_libre(position_x, largeur)

            # Crée la forme
            match forme:
                case "triangle_inversé":
                    carte._creer_triangle_inverse(position_x, hauteur_base, largeur, hauteur, type_tuile)
                case "triangle_normal":
                    carte._creer_triangle_normal(position_x, hauteur_base, hauteur, type_tuile)
                case "pont":
                    carte._creer_pont(position_x, hauteur_base, largeur, type_tuile)
                case "triangle_vertical":
                    carte._creer_triangle_vertical(position_x, hauteur_base, largeur, hauteur, type_tuile)
                case "escalier":
                    carte._creer_escalier(position_x, hauteur_base, hauteur, type_tuile)
                case "rectangle":
                    carte._creer_rectangle(position_x, hauteur_base, largeur, hauteur, type_tuile)

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
                carte.ajouter_ennemis()
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
    # endregion