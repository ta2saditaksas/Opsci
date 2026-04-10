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
- **Conteneurisation** : Docker
- **Orchestration** : Kubernetes (Minikube)
- **CI/CD** : GitLab CI/CD

## Structure du projet
- `frontend/` : Interface utilisateur (HTML + CSS + JS)
- `backend/` : API Backend avec FastAPI
- `database/` : Scripts SQL pour PostgreSQL
- `k8s/` : Manifests Kubernetes pour déploiement
- `docs/` : Documentation et schémas
- `README.md` : Fichier de documentation
- `.gitlab-ci.yml` : Pipeline CI/CD pour automatisation

## Fonctionnalités
### Minimales
- Catalogue de films dynamique (TMDB API)
- Barre de recherche pour trouver des films
- Communication front-end / back-end via API
- Gestion minimale des erreurs

### Avancées
- Films favoris (ajout / suppression)
- Stockage des favoris en PostgreSQL

## Lancer avec Docker Compose

### Prérequis
- Docker Desktop installé
- Un token TMDB ([obtenir ici](https://www.themoviedb.org/settings/api))

### Démarrage
```bash
git clone https://gitlab.com/opsci_2026/opsci
cd opsci
echo "TMDB_TOKEN=ton_token_ici" > .env
docker compose up --build
```
- Frontend : http://localhost:8080
- Backend : http://localhost:8000

## Lancer avec Kubernetes (Minikube)

### Prérequis
- Minikube + kubectl + Docker installés

### Démarrage
```bash
minikube start
eval $(minikube docker-env)
docker build -t opsci-backend ./backend
docker build -t opsci-frontend ./frontend
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
minikube service frontend-service --url
```

## Pipeline CI/CD
Le pipeline se déclenche automatiquement à chaque push :
1. **test** — vérification des fichiers
2. **build** — construction des images Docker
3. **deploy** — déploiement (branche main)

## Architecture
```
[Navigateur] → [Frontend :8080] → [Backend :8000] → [PostgreSQL :5432]
                                        ↓
                                   [TMDB API]
```