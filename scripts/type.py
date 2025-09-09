"""Définitions des types utilisés dans le projet de génération procédurale.

Ce module définit les types personnalisés pour améliorer la lisibilité et la sécurité de type.
"""

from typing import Any, Dict, List, Literal, Optional, Tuple, TypeAlias

# Types de base du jeu
TypeTuile: TypeAlias = Literal["herbe", "pierre"]

# Types pour les ressources et données
# Dict[str, List[pygame.Surface]] pour les ressources graphiques
# Dict[str, Tuile] pour la carte
# Optional[pygame.Color] pour les couleurs
# Tuple[int, int] pour les positions