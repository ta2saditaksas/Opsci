#!/bin/bash

echo "Lancement de T&A Screen..."

# Vérifier que .env existe
if [ ! -f .env ]; then
  echo "Fichier .env manquant !"
  echo "Créez un fichier .env avec : TMDB_TOKEN=votre_token"
  exit 1
fi

# Lancer Docker Compose
echo "Démarrage des conteneurs..."
docker compose up --build -d

echo ""
echo "T&A Screen est lancé !"
echo "Frontend : http://localhost:8080"
echo "Backend  : http://localhost:8000"
echo ""
echo "Pour arrêter : docker compose down"