"""Définitions des types utilisés dans le projet de génération procédurale.

Ce module définit les types personnalisés pour améliorer la lisibilité et la sécurité de type.
"""

from typing import Literal, TypeAlias

TypeTuile: TypeAlias = Literal["herbe", "pierre"]
TypeDecoration: TypeAlias = Literal["arbre", "plante"]
TypeElement: TypeAlias = TypeTuile | TypeDecoration