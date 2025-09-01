from typing import Any, Optional
import pygame

pygame.font.init()
police = pygame.font.Font(None, 30)
ecran = pygame.display.get_surface()

def deboguer(info: object,*, x: int = 0, y: int = 0, couleur: Any = "black", antialias:bool = False, wraplength: Optional[int] = 0, alignement:int = pygame.FONT_LEFT):
    ecran = pygame.display.get_surface()
    police.align = alignement
    surf_texte = police.render(str(info), antialias, couleur, wraplength=wraplength if wraplength else ecran.get_width())
    ecran.blit(surf_texte, (x, y))


def deboguer_img(img: pygame.Surface, x: int = 0, y: int = 0):
    ecran = pygame.display.get_surface()
    ecran.blit(img, (x, y))
