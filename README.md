# Projet OpsCi 2026

## Amel BEN CHABANE 21304456
## Tassadit AKSAS 21302943

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
- **Backend** : FastAPI
- **Base de données** : PostgreSQL
- **Conteneurisation** : Docker
- **Orchestration** : Kubernetes
- **CI/CD** : GitLab CI/CD

## Structure du projet
- `frontend/` : Interface utilisateur (HTML + CSS + JS)
- `backend/` : API Backend avec FastAPI
- `database/` : Scripts SQL pour PostgreSQL
- `k8s/` :  Kubernetes pour déploiement
- `docs/` : Documentation et schémas
- `README.md` : Fichier de documentation
- `.gitlab-ci.yml` : Pipeline CI/CD pour automatisation

## Fonctionnalités
### Fonctionnalités minimales
- Catalogue de films dynamique
- Barre de recherche pour trouver des films
- Communication front-end / back-end via API 
- Gestion minimale des erreurs

### Fonctionnalités avancées 
- Films favoris
- Pagination des résultats
- Cache
- Recherche avancée
