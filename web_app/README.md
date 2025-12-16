# Job Board - Application de Visualisation d'Offres d'Emploi

Application web moderne pour visualiser et filtrer des offres d'emploi avec un score IA.

## Fonctionnalités

- **Affichage en liste** : Liste d'offres à gauche avec titre, entreprise et score IA
- **Vue détaillée** : Panneau de détails à droite avec description complète et liens
- **Filtrage par date** : Sélecteur de date pour voir les offres d'un jour spécifique
- **Score IA coloré** : Code couleur du vert (bon match) au rouge (mauvais match)
- **Tri automatique** : Offres triées par score IA croissant (meilleurs scores en premier)
- **Design moderne** : Interface inspirée de LinkedIn avec un style éditorial professionnel

## Installation

Avec Python 3.13.9.

Installer les dépendances Python :
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Attention: modifier le path vers la database dans app.py (dans `get_db_connection`).

## Lancement

```bash
python app.py
```

L'application sera accessible sur : http://localhost:5000

## Utilisation

1. **Sélectionner une date** : Utilisez le sélecteur de date en haut à droite
2. **Parcourir les offres** : Cliquez sur une offre dans la liste de gauche
3. **Voir les détails** : Les détails s'affichent dans le panneau de droite
4. **Postuler** : Cliquez sur les boutons pour accéder aux offres originales

## Code Couleur des Scores IA

- **Vert foncé** (< 0.15) : Excellent match - À privilégier
- **Vert** (0.15-0.20) : Bon match - Intéressant
- **Orange** (0.20-0.30) : Match moyen
- **Orange foncé** (0.30-0.40) : Match faible
- **Rouge** (> 0.40) : Mauvais match

Plus le score est bas, meilleur est le match selon l'algorithme IA.

## Technologies utilisées

- **Backend** : Flask (Python)
- **Frontend** : HTML, CSS, JavaScript vanilla
- **Base de données** : SQLite

## API Endpoints

- `GET /` : Page principale de l'application
- `GET /api/dates` : Liste des dates disponibles dans la base
- `GET /api/jobs?date=YYYY-MM-DD&include_internships=<true|false>` : Offres d'emploi pour une date donnée avec ou sans offre de stage
