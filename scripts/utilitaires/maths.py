"""Module utilitaire pour les fonctions mathématiques."""

def signe(nombre: float) -> int:
    """Retourne le signe d'un nombre.

    Args:
        nombre (float): Nombre dont on veut connaître le signe

    Returns:
        int: -1 si négatif, 0 si nul, 1 si positif
    """
    return int(nombre / abs(nombre))