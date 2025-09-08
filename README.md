# 🌐 Génération procédurale de cartes

## 📝 Description

🐍 Projet [Python](https://www.python.org/) utilisant [Pygame](https://www.pygame.org/news) 🎮 pour générer et afficher des cartes procédurales sous forme de tuiles 🟫.
Le système crée automatiquement un ensemble de tuiles 🛤️ en fonction de probabilités aléatoires 🎲, remplit les zones vides et fermées 🔐 et permet de naviguer dans la carte générée 🗺️.

L’objectif est de fournir un éditeur simple et extensible 🛠️ pour explorer les techniques de génération procédurale 🌪️.

---

## 🏗️ Structure du projet

📂 La structure du projet est organisée de manière modulaire pour faciliter la maintenance et l'extension.

```tree
.
│   main.py                       # Point d'entrée du programme (éditeur Pygame) 🚀
│
├───rsc/                          # Dossier des ressources graphiques 🖼️
│   ├───images/                   # Tous les sprites utilisés par l'application 🎨
│   └───cartes/                   # Sauvegarde des cartes générées (fichiers JSON) 💾
│
├───scripts/                      # Modules Python principaux 📜
│   │   carte.py                  # Gestion et rendu de la carte complète 🗺️
│   │   tuile.py                  # Classe et logique des tuiles individuelles 🟫
│   │   type.py                   # Définitions des types utilisés 🏷️
│   │
│   ├───parametres/               # Paramètres globaux de l'application (constantes) ⚙️
│   │
│   └───utilitaires/              # Outils auxiliaires 🛠️
```

### Détails des composants principaux :

* **main.py** 🚀 : Lance l'application Pygame et gère la boucle principale.
* **scripts/carte.py** 🗺️ : Contient la logique de génération procédurale et d'affichage de la carte.
* **scripts/tuile.py** 🟫 : Définit les propriétés et comportements des tuiles (herbe, pierre, etc.).
* **rsc/** 🖼️ : Stocke toutes les ressources visuelles nécessaires au rendu.
* **scripts/utilitaires/** 🛠️ : Fournit des fonctions réutilisables pour le débogage, les maths et la gestion d'images.

---

## ⚙️ Fonctionnalités

### 🌪️ Génération procédurale

* **Chemin aléatoire** 🛤️ : Crée automatiquement un chemin continu avec probabilités configurables.
* **Remplissage intelligent** 🧠 : Remplit automatiquement les zones fermées avec des tuiles appropriées.
* **Variabilité infinie** 🎲 : Chaque génération produit une carte unique grâce aux graines aléatoires.

### 🖥️ Affichage et interaction

* **Rendu temps réel** ⚡ : Affiche les cartes de façon fluide et interactive.
* **Navigation fluide** 🧭 : Déplacez-vous dans la carte avec les touches directionnelles.
* **Regénération instantanée** 🔄 : Génère une nouvelle carte avec une touche.
* **Affichage des statistiques** 📊 : Visualise les paramètres de génération en temps réel.

### 📋 Exemples d'utilisation

* **Test de paramètres** 🧪 : Modifie les probabilités pour observer l’effet sur le chemin.
* **Sauvegarde** 💾 : Sauvegarde les cartes en JSON pour analyse ultérieure.

---

## ⌨️ Contrôles

### 🧭 Navigation et génération

| Touche                         | Action                        | Description                           |
| ------------------------------ | ----------------------------- | ------------------------------------- |
| `Flèches directionnelles ↑↓←→` | ➡️ Déplacer la vue            | Permet de naviguer dans la carte.     |
| `N`                            | 🆕 Créer une nouvelle carte   | Génère une carte vide.                |
| `P`                            | 🔄 Générer carte continue     | Génère une carte avec chemin continu. |
| `I`                            | 🏝️ Générer une carte en îles  | Crée une carte organisée en îles.       |
| `O`                            | 📂 Charger une carte          | Ouvre un fichier JSON de carte.       |
| `S`                            | 💾 Sauvegarder la carte          | Sauvegarde la carte actuelle en JSON. |

---

## 📋 Exemples d'utilisation

* Clonez le repo 📥
* Placez-vous dans le dossier principal 📂
* Lancez le programme 🚀
* Utilisez `P` pour générer et les flèches pour explorer ➡️
* Sauvegardez avec `S` 💾 ou ouvrez une carte avec `O` 📂

---

## 💻 Commande de base

```bash
git clone https://github.com/Dosz-Benito/Raydash.git
cd ./Raydash
python main.py
```

---

## 🔮 Extensions possibles

* Ajouter d’autres types de tuiles (eau 🌊, sable 🏖️, roche 🏔️).
* Implémenter des algorithmes de bruit (Perlin, Simplex) 🌪️.
* Export vers d’autres moteurs (Unity 🎮, Godot 🕹️).

---

## 👨‍💻 Auteur

Développé par **do SANTOS ZOUNON Bénito K.** (projet privé).

---