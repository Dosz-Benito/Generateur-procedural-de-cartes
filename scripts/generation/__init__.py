from typing import Literal
from ..carte import Carte
from .generateur_carte import GenerateurCarte
from ..parametres import NOMBRE_TUILES


generateur_terrain: GenerateurCarte = GenerateurCarte(NOMBRE_TUILES)

def generer_carte(type_terrain: Literal["Ile", "Bloc"]) -> Carte:
    """Génère une nouvelle carte complète, avec les tuiles, la décoration, le joueur et les ennemis.

    Args:
        type_terrain (Literal[&quot;Ile&quot;, &quot;Bloc&quot;]): Le type de terrain à utiliser pour la génération.
    """
    carte = generateur_terrain.generer(type_terrain)
    return carte