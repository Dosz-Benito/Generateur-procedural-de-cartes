import random
from typing import Literal
from scripts.parametres import DECALAGE_BAS, DECALAGE_DROITE, DECALAGE_GAUCHE, DECALAGE_HAUT, NOMBRE_TUILES, TypeTuile


class GenerateurTerrain:
    def __init__(self, carte) -> None:
        self.carte = carte
        self.nombre_tuiles: int = NOMBRE_TUILES
        self.probabilite_monter: float = 0.0
        self.probabilite_gauche: float = 0.0

    def generer(self, type_carte: Literal["Ile", "Bloc"]) -> None:
        """Génère le terrain de la carte selon le type de génération demandé.

        Args:
            type_carte (Literal["Ile", "Bloc"]): Type de génération à utiliser.
        """
        match type_carte:
            case "Ile":
                self.generation_procedurale_iles()
            case "Bloc":
                self.generation_procedurale_bloc()
            case _:
                raise ValueError(f"Le type de carte {type_carte} n'est pas pris en charge")

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
