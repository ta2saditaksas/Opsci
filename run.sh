#!/bin/bash

echo "🚀 Lancement de T&A Screen..."

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé"
    exit 1
fi

# Vérifier que le token TMDB est présent
if [ ! -f .env ]; then
    echo "Fichier .env manquant"
    echo "Créez un fichier .env avec : TMDB_TOKEN=votre_token"
    exit 1
fi

echo "Docker trouvé"
echo "Fichier .env trouvé"

# Lancer Docker Compose
echo "Lancement des conteneurs..."
docker compose up --build -d

echo ""
echo "Application lancée !"
echo "Frontend : http://localhost:8080"
echo "Backend  : http://localhost:8000"
echo ""
echo "Pour arrêter : docker compose down"