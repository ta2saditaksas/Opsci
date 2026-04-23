# Projet OpsCi 2026
Amel BEN CHABANE 21304456  
Tassadit AKSAS 21302943

## Description
Projet de conception et déploiement d'une application web orientée données et API. Ce projet comprend une interface utilisateur affichant un catalogue de films, un backend exposant une API, et une base de données pour stocker les informations.

## Objectifs
- Afficher un catalogue de films dynamique
- Intégrer une barre de recherche
- Utiliser une architecture front-end / back-end / base de données
- Conteneuriser l'application avec Docker
- Déployer l'application via Kubernetes
- Automatiser les tests et le déploiement avec GitLab CI/CD

## Stack utilisée
- **Frontend** : HTML, CSS, JavaScript (sans framework)
- **Backend** : FastAPI (Python)
- **Base de données** : PostgreSQL
- **Source de données** : API TMDB
- **Conteneurisation** : Docker
- **Orchestration** : Kubernetes (Minikube)
- **CI/CD** : GitLab CI/CD

## Structure du projet
opsci/
├── backend/app/main.py      # API FastAPI
├── backend/tests/           # Tests unitaires pytest
├── backend/Dockerfile
├── backend/requirements.txt
├── frontend/index.html
├── frontend/script.js
├── frontend/style.css
├── frontend/favicon.svg
├── k8s/                     # Manifests Kubernetes
├── docker-compose.yml
├── .gitlab-ci.yml
├── run.sh                   # Script de lancement
└── README.md


## Fonctionnalités
### Minimales
- Catalogue de films dynamique (TMDB API)
- Barre de recherche pour trouver des films
- Communication front-end / back-end via API
- Gestion minimale des erreurs

### Avancées
- Favoris par profil utilisateur (PostgreSQL)
- Recommandations basées sur les favoris
- Historique de visionnage
- Films tendances du jour
- Filtres par humeur et par genre
- Bande annonce YouTube (modal)
- Pagination du catalogue
- Cache Redis (performances)
- Profils utilisateurs avec avatars colorés
- Splash screen 

## Lancement rapide

### Prérequis
- Docker + Docker Compose installés
- Token TMDB gratuit : https://www.themoviedb.org/settings/api

### Démarrage
```bash
git clone https://gitlab.com/opsci_2026/opsci
cd opsci
echo "TMDB_TOKEN=ton_token_ici" > .env
./run.sh
```

- **Frontend** : http://localhost:8080
- **Backend API** : http://localhost:8000

### Arrêt
```bash
docker compose down        # Garde les données
docker compose down -v     # Supprime les données
```

## Déploiement Kubernetes (Minikube)

```bash
minikube start --cpus=1 --force
eval $(minikube docker-env)
docker build -t opsci-backend ./backend
docker build -t opsci-frontend ./frontend
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
kubectl port-forward service/frontend-service 8080:8080
```

## Pipeline CI/CD
Le pipeline se déclenche automatiquement à chaque push :
1. **test_files** — vérification de la présence des fichiers
2. **test_backend** — tests unitaires pytest
3. **build** — construction des images Docker
4. **deploy** — déploiement simulé (branche main uniquement)

## Architecture
```
[Navigateur] → [Frontend :8080] → [Backend :8000] → [PostgreSQL :5432]
                                        ↓
                                   [TMDB API]
```