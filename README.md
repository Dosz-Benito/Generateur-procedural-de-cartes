# Génération procédurale de cartes

## 📝 Description

Projet Python utilisant **Pygame** pour générer et afficher des cartes procédurales sous forme de tuiles.
Le système crée automatiquement un chemin en fonction de probabilités aléatoires, remplit les zones fermées et permet de naviguer dans la carte générée.

L’objectif est de fournir un éditeur simple et extensible pour explorer les techniques de génération procédurale.

---

## 📂 Structure du projet

```
.
│   main.py                       # Point d'entrée du programme (éditeur Pygame)
│   .gitignore
│   Génération procédurale.code-workspace
│
├───rsc/                          # Ressources graphiques
│   └───herbe/                    # Sprites de tuiles d'herbe
│       0.png ... 8.png
│
├───scripts/
│   │   carte.py                  # Gestion et rendu de la carte
│   │   tuile.py                  # Classe et logique des tuiles
│   │
│   ├───parametres/               # Raccourcis clavier, constantes, tailles
│   │   __init__.py
│   │
│   └───utilitaires/
│       debogage.py               # Outils pour afficher du texte de debug
│       maths.py                  # Fonctions mathématiques utiles
│       outils_images.py          # Chargement et manipulation d’images
│
└───.vscode/
    tasks.json                    # Configuration VS Code
```

---

## 🎮 Fonctionnalités

* Génération procédurale d’un chemin avec probabilités configurables.
* Remplissage automatique des zones fermées.
* Affichage temps réel avec **Pygame**.
* Navigation dans la carte.
* Regénération de la carte par une simple touche.
* Affichage des statistiques utilisées.

---

## ⌨️ Contrôles

* **Touche `P`** → regénérer une carte avec de nouvelles statistiques aléatoires.
* **Touches directionnelles** → Naviguer dans la carte générée.

---

## 🔮 Extensions possibles

* Ajouter d’autres biomes (eau, sable, roche, etc.).
* Implémenter des algorithmes de bruit (Perlin, Simplex).
* Sauvegarder/charger les cartes en JSON ou images.
* Export vers d’autres moteurs (Unity, Godot).

---

## 👤 Auteur

Développé par **do SANTOS ZOUNON Bénito K.** (projet privé).

---