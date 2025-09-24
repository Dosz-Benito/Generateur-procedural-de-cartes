# Documentation Technique - Générateur Procédural de Cartes

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du projet](#architecture-du-projet)
3. [Modules et classes](#modules-et-classes)
4. [Algorithmes de génération](#algorithmes-de-génération)
5. [Installation et dépendances](#installation-et-dépendances)
6. [Guide d'utilisation](#guide-dutilisation)
7. [API et référence des fonctions](#api-et-référence-des-fonctions)
8. [Extensions possibles](#extensions-possibles)

---

## 🎯 Vue d'ensemble

Ce projet implémente un **générateur procédural de cartes** utilisant Python et Pygame. Le système génère automatiquement des cartes sous forme de grille de tuiles en utilisant des algorithmes probabilistes pour créer des chemins organiques et remplir les espaces fermés.

### Fonctionnalités principales

- **Génération procédurale** : Création automatique de chemins basée sur des probabilités
- **Auto-tiling** : Sélection automatique des sprites appropriés selon le contexte
- **Remplissage intelligent** : Comblement automatique des zones fermées
- **Navigation temps réel** : Déplacement fluide dans la carte générée
- **Régénération dynamique** : Création de nouvelles cartes à la volée
- **Interface de débogage** : Affichage des statistiques et informations de développement

---

## 🏗️ Architecture du projet

```
Génération procédurale de cartes/
│
├── main.py                           # Point d'entrée - Classe Editeur
├── README.md                         # Documentation utilisateur
├── DOCUMENTATION.md                  # Documentation technique (ce fichier)
│
├── rsc/                              # Ressources graphiques
│   └── herbe/                        # Sprites de tuiles (0.png à 8.png)
│       ├── 0.png ... 8.png
│
└── scripts/                          # Code source principal
    ├── carte.py                      # Gestion de la carte et auto-tiling
    ├── tuile.py                      # Classe Tuile individuelle
    │
    ├── parametres/                   # Configuration et constantes
    │   └── __init__.py               # Touches, tailles, décalages
    │
    └── utilitaires/                  # Modules utilitaires
        ├── debogage.py               # Affichage de texte de debug
        ├── maths.py                  # Fonctions mathématiques
        └── outils_images.py          # Chargement d'images
```

### Flux de données

```
main.py (Editeur)
    ↓
    ├── Carte ← Tuile
    ├── Ressources (images)
    └── Utilitaires (debug, maths, images)
```

---

## 🧩 Modules et classes

### 1. `main.py` - Classe Editeur

**Responsabilité** : Point d'entrée principal, gestion de l'interface Pygame et orchestration du système.

```python
class Editeur:
    def __init__(self) -> None
    def generation_procedurale(self) -> None
    def generation_procedurale_iles(self) -> None
    def lancer(self) -> NoReturn
    def appliquer_decalage(self) -> None
    def tout_effacer(self) -> None
```

**Attributs clés** :
- `surface_affichage` : Surface de rendu interne (900x430)
- `fenetre` : Fenêtre d'affichage mise à l'échelle
- `ressources` : Dictionnaire des ressources graphiques
- `carte` : Instance de la classe Carte
- `decalage_camera` : Position de la caméra
- `probabilite_monter`, `probabilite_gauche` : Probabilités de génération

### 2. `scripts/carte.py` - Classe Carte

**Responsabilité** : Gestion de la grille de tuiles, auto-tiling et algorithmes de remplissage.

```python
class Carte:
    def __init__(self, editeur: Any, taille: int = 16) -> None
    def tuile_presente(self, position: Sequence[int]) -> bool
    def ajouter_tuile(self, x: int, y: int, type_tuile: TypeTuile) -> None
    def enlever_tuile(self, x: int, y: int) -> None
    def entourer(self, tuile: Tuile) -> None
    def redessiner(self) -> None
    def afficher(self, surface: pygame.Surface, decalage_camera: pygame.Vector2) -> None
    def enregistrer_carte(self) -> tuple[bool, str]
    def charger_carte(self) -> tuple[bool, str]
    def nouvelle_carte(self) -> tuple[bool, str]
```

**Constantes importantes** :
- `CARTE_REDESSIN` : Mapping des configurations de voisinage vers les indices de sprites
- `TYPES_REDESSIN` : Types de tuiles supportant l'auto-tiling

### 3. `scripts/tuile.py` - Classe Tuile

**Responsabilité** : Représentation d'une tuile individuelle avec ses propriétés et méthodes d'affichage.

```python
class Tuile:
    def __init__(self, type: Literal["herbe"], pos: tuple[int, int], index: int, images: list[pygame.Surface])
    def afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None
    def tuiles_autour(self, carte) -> list[Tuile]
```

**Attributs** :
- `type` : Type de tuile ("herbe" actuellement)
- `pos` : Position [x, y] dans la grille
- `index` : Index du sprite à utiliser (0-8)
- `images` : Liste des sprites disponibles

### 4. `scripts/parametres/__init__.py`

**Responsabilité** : Configuration globale du projet.

**Constantes de configuration** :
```python
AGRANDISSEMENT = 2.0
TAILLE_AFFICHAGE = (900, 430)
TAILLE_ECRAN = (1800, 860)  # Calculé automatiquement

# Contrôles
DECALER_GAUCHE = pygame.K_LEFT
DECALER_DROITE = pygame.K_RIGHT
DECALER_HAUT = pygame.K_UP
DECALER_BAS = pygame.K_DOWN
GENERER_CARTE = pygame.K_p

# Décalages directionnels
INDEXS_DECALAGES_DROITS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
INDEXS_DECALAGES_DIAGONAUX = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
```

### 5. Modules utilitaires

#### `scripts/utilitaires/debogage.py`
```python
def afficher_debug(information: str | int | float, *, x: int = 0, y: int = 0, couleur: pygame.Color = pygame.Color("white"), antialias: bool = False, wraplength: Optional[int] = 0, alignement: int = pygame.FONT_LEFT) -> None
def afficher_image_debug(image: pygame.Surface, x: int = 0, y: int = 0) -> None
```

#### `scripts/utilitaires/maths.py`
```python
def signe(nombre: float) -> int  # Retourne -1, 0, ou 1
```

#### `scripts/utilitaires/outils_images.py`
```python
def charger_image(fichier: str, couleur_transparente: tuple[int, int, int] = (0, 0, 0)) -> pygame.Surface
def charger_images(dossier: str, couleur_transparente: tuple[int, int, int] = (0, 0, 0)) -> list[pygame.Surface]
```

---

## 🎲 Algorithmes de génération

### 1. Génération procédurale du chemin principal

L'algorithme utilise une **marche aléatoire biaisée** :

```python
def generation_procedurale(self) -> None:
    x = n_x = 0
    y = n_y = 0
    self.p_haut = random.random()      # Probabilité de monter
    self.p_gauche = random.random()    # Probabilité d'aller à gauche
    
    for _ in range(500):  # 500 tuiles à placer
        while self.carte.tuile_presente((n_x, n_y)):
            # Choix de direction basé sur les probabilités
            if random.random() < self.p_gauche:
                n_x += DEC_GAUCHE[0]  # -1
            else:
                n_x += DEC_DROITE[0]  # +1
                
            if random.random() < self.p_haut:
                n_y += DEC_HAUT[1]    # -1
            else:
                n_y += DEC_BAS[1]     # +1
        
        self.carte.ajouter_tuile(n_x, n_y)
```

**Caractéristiques** :
- **Probabilités fixes** par génération pour créer des tendances cohérentes
- **Évitement des collisions** : continue jusqu'à trouver une position libre
- **Chemin organique** : les probabilités créent des directions préférentielles

### 2. Algorithme de remplissage intelligent

La méthode `entourer()` analyse le voisinage de chaque tuile pour combler les espaces fermés :

```python
def entourer(self, tuile: Tuile):
    # Analyse des voisins directs (haut, bas, gauche, droite)
    tuiles_autour_droit = [...]
    nb_tuiles_autour_droit = len(tuiles_autour_droit)
    
    # Analyse des voisins diagonaux
    tuiles_autour_diagonales = [...]
    nb_tuiles_autour_diagonales = len(tuiles_autour_diagonales)
    
    # Logique de remplissage basée sur le nombre de voisins
    match nb_tuiles_autour_droit:
        case 0: # Tuile isolée
            # Différentes stratégies selon les voisins diagonaux
        case 1: # Tuile avec un voisin direct
            # Remplissage conditionnel
        # ... autres cas
```

**Stratégies de remplissage** :
- **Tuiles isolées** : Suppression ou connexion selon le contexte
- **Espaces fermés** : Remplissage automatique des zones entourées
- **Profondeur** : Ajout de tuiles en profondeur pour certaines configurations

### 3. Système d'auto-tiling

Le système sélectionne automatiquement le bon sprite selon la configuration des voisins :

```python
CARTE_AUTOTUILES = {
    tuple(sorted([(0, 1), (1, 0)])): 0,           # Coin haut-gauche
    tuple(sorted([(-1, 0), (1, 0), (0, 1)])): 1, # Bord haut
    tuple(sorted([(-1, 0), (0, 1)])): 2,          # Coin haut-droite
    # ... 9 configurations au total
}
```

**Processus** :
1. Pour chaque tuile, analyser les 4 voisins directs
2. Créer un tuple trié des décalages des voisins présents
3. Chercher la configuration dans `CARTE_AUTOTUILES`
4. Assigner l'index de sprite correspondant

---

## 💻 Installation et dépendances

### Prérequis

- **Python 3.8+** (utilise les annotations de type modernes)
- **Pygame 2.0+** pour l'affichage et les événements

### Installation

```bash
# Cloner le projet
git clone https://github.com/Dosz-Benito/Generateur-procedural-de-cartes.git
cd Generateur-procedural-de-cartes

# Installer les dépendances
pip install pygame

# Lancer le projet
python main.py
```

### Structure des ressources

Le dossier `rsc/herbe/` doit contenir 9 images PNG numérotées de 0 à 8 :
- `0.png` : Coin haut-gauche
- `1.png` : Bord haut
- `2.png` : Coin haut-droite
- `3.png` : Bord droit
- `4.png` : Coin bas-droite
- `5.png` : Bord bas
- `6.png` : Coin bas-gauche
- `7.png` : Bord gauche
- `8.png` : Centre/remplissage

---

## 🎮 Guide d'utilisation

### Contrôles

| Touche | Action |
|--------|--------|
| `P` | Générer une nouvelle carte |
| `↑↓←→` | Naviguer dans la carte |
| `Échap` | Quitter (fermer la fenêtre) |

### Interface de débogage

L'écran affiche en temps réel :
- **Probabilités de génération** : Pourcentages de chance de monter et d'aller à gauche
- **État des mouvements** : Touches directionnelles actuellement pressées
- **Informations de développement** : Messages d'erreur et de debug

### Workflow typique

1. **Lancement** : `python main.py`
2. **Observation** : La carte initiale se génère automatiquement
3. **Navigation** : Utiliser les flèches pour explorer
4. **Régénération** : Appuyer sur `P` pour une nouvelle carte
5. **Analyse** : Observer les probabilités affichées pour comprendre la génération

---

## 📚 API et référence des fonctions

### Classe Editeur

#### `__init__(self) -> None`
Initialise l'éditeur Pygame, charge les ressources et génère la première carte.

#### `generation_procedurale(self) -> None`
Génère une nouvelle carte en utilisant l'algorithme de marche aléatoire.
- Définit de nouvelles probabilités aléatoirement
- Place 500 tuiles selon ces probabilités
- Appelle le remplissage et le redessin

#### `remplir(self) -> None`
Lance l'algorithme de remplissage sur toutes les tuiles existantes.

#### `lancer(self) -> NoReturn`
Boucle principale du jeu :
- Gestion des événements clavier
- Mise à jour de l'affichage
- Gestion du déplacement de la caméra

### Classe Carte

#### `tuile_presente(self, pos: Sequence[int]) -> bool`
Vérifie si une tuile existe à la position donnée.

#### `ajouter_tuile(self, x: int, y: int) -> None`
Ajoute une nouvelle tuile de type "herbe" à la position spécifiée.

#### `entourer(self, tuile: Tuile) -> None`
Analyse le voisinage d'une tuile et applique les règles de remplissage.

#### `redessiner(self) -> None`
Met à jour les indices de sprites de toutes les tuiles selon leur voisinage.

### Classe Tuile

#### `afficher(self, surface: pygame.Surface, decalage: pygame.Vector2) -> None`
Dessine la tuile sur la surface donnée en tenant compte du décalage de caméra.

### Fonctions utilitaires

#### `charger_images(dossier: str, couleur_transparente: tuple[int, int, int] = (0, 0, 0)) -> list[pygame.Surface]`
Charge toutes les images PNG d'un dossier et retourne une liste triée.

#### `afficher_debug(information: str | int | float, **kwargs) -> None`
Affiche du texte de débogage à l'écran avec options de formatage.

---

## 🚀 Extensions possibles

### 1. Nouveaux biomes

```python
# Ajouter dans parametres/__init__.py
TYPES_BIOMES = ["herbe", "eau", "sable", "pierre", "neige"]

# Modifier Tuile.__init__
def __init__(self, type: Literal["herbe", "eau", "sable", "pierre", "neige"], ...):
```

### 2. Génération par bruit de Perlin

```python
import noise

def generer_avec_perlin(self, largeur: int, hauteur: int):
    for x in range(largeur):
        for y in range(hauteur):
            valeur = noise.pnoise2(x/10.0, y/10.0)
            if valeur > 0.1:
                self.ajouter_tuile(x, y)
```

### 3. Sauvegarde/chargement

```python
import json

def sauvegarder_carte(self, fichier: str):
    data = {
        "tuiles": [(t.pos, t.type, t.index) for t in self.carte.values()],
        "probabilites": (self.p_haut, self.p_gauche)
    }
    with open(fichier, 'w') as f:
        json.dump(data, f)

def charger_carte(self, fichier: str):
    with open(fichier, 'r') as f:
        data = json.load(f)
    # Reconstruire la carte...
```

### 4. Optimisations de performance

- **Culling de frustum** : Ne dessiner que les tuiles visibles
- **Chunking** : Diviser la carte en sections pour un chargement dynamique
- **Cache de sprites** : Éviter les rechargements d'images

### 5. Interface utilisateur avancée

- **Menu de configuration** : Ajuster les probabilités en temps réel
- **Outils d'édition** : Placer/supprimer des tuiles manuellement
- **Minimap** : Vue d'ensemble de la carte générée

### 6. Export vers d'autres formats

```python
def exporter_png(self, fichier: str):
    # Créer une surface de la taille totale de la carte
    # Dessiner toutes les tuiles
    # Sauvegarder en PNG

def exporter_json_unity(self, fichier: str):
    # Format compatible avec Unity Tilemap
    pass
```

---

## 🐛 Débogage et développement

### Messages de debug courants

- `"Une tuile est au milieu de nulle part !!!"` : Tuile isolée détectée
- `"Index adéquat introuvable"` : Configuration de voisinage non reconnue

### Outils de développement

- Utiliser `debogage.deboguer()` pour afficher des informations
- Modifier les probabilités dans `generation_procedurale()` pour tester
- Ajuster `CARTE_AUTOTUILES` pour de nouvelles configurations

### Tests recommandés

1. **Test de génération** : Vérifier que 500 tuiles sont bien placées
2. **Test d'auto-tiling** : Toutes les tuiles doivent avoir un index valide
3. **Test de performance** : Mesurer le temps de génération et d'affichage
4. **Test de navigation** : Vérifier la fluidité du déplacement

---

## 📄 Licence et contribution

Projet développé par **do SANTOS ZOUNON Bénito K.**

Pour contribuer :
1. Impossible de contribuer, projet strictement personnel 😬😉🤪😅🙏😎

---
