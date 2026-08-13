from typing import Any, Iterable
import pygame
from pygame.sprite import AbstractGroup

class Rendu(pygame.sprite.Group):
    def __init__(self, largeur_ecran: int, hauteur_ecran: int, *sprites: Any | AbstractGroup | Iterable) -> None:
        super().__init__(*sprites)
        self.decalage = pygame.Vector2()
        self.largeur_ecran: int = largeur_ecran
        self.hauteur_ecran: int = hauteur_ecran

    def centrer(self, cible: pygame.sprite.Sprite) -> None:
        """Centre la caméra sur le sprite cible (ex: joueur)."""
        self.decalage.x = cible.rect.centerx - self.largeur_ecran // 2  # pyright: ignore[reportOptionalMemberAccess]
        self.decalage.y = cible.rect.centery - self.hauteur_ecran // 2  # pyright: ignore[reportOptionalMemberAccess]

    def deplacer(self, dx: float, dy: float) -> None:
        """Déplace la caméra de dx, dy pixels."""
        self.decalage.x += dx
        self.decalage.y += dy

    def draw(self, surface: pygame.Surface) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Dessine uniquement les sprites visibles en tenant compte du décalage de la caméra."""
        for sprite in self.sprites():
            # Calculer le rect décalé
            rect_decale: pygame.Rect = sprite.rect.move(-self.decalage.x, -self.decalage.y)

            # Vérifier si le sprite est visible dans la fenêtre
            if (rect_decale.right >= 0 and rect_decale.left <= self.largeur_ecran and
                rect_decale.bottom >= 0 and rect_decale.top <= self.hauteur_ecran):
                surface.blit(sprite.image, rect_decale)