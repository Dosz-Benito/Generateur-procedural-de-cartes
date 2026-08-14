"""Module définissant la classe Bloc pour regrouper les tuiles marchables."""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.tuile import Tuile


@dataclass
class BlocTuiles:
    """Représente un groupe(bloc) de tuiles marchables à la même hauteur et contiguës.

    Un bloc correspond à une plateforme continue : toutes ses tuiles sont sur la
    même ligne (même y) et se suivent horizontalement sans espace vide entre.
    """

    tuiles: list[Tuile]
    y: float
    x_min: float
    x_max: float

    @property
    def milieu(self) -> float:
        """Position X du centre du bloc en pixels."""
        return (self.x_min + self.x_max) / 2

    @property
    def nb_tuiles(self) -> int:
        """Le nombre de tuiles que contient ce bloc"""
        return len(self.tuiles)

    @classmethod
    def depuis_tuiles(cls, tuiles: list[Tuile]) -> BlocTuiles:
        """Construit un bloc à partir de tuiles contiguës à la même hauteur.

        Args:
            tuiles (list[Tuile]): Tuiles contiguës du bloc

        Returns:
            Bloc: Nouveau bloc regroupant ces tuiles
        """
        positions_x: list[float] = [tuile.rect.x for tuile in tuiles]
        return cls(
            tuiles,
            tuiles[0].rect.y,
            min(positions_x),
            max(positions_x)
        )