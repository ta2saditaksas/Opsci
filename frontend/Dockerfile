FROM python:3.12-slim

WORKDIR /app

COPY . .

# Script de démarrage qui génère config.js avec l'URL du backend
CMD sh -c "echo \"const API_BASE = '${BACKEND_URL:-http://localhost:8000}';\" > /app/config.js && python3 -m http.server 8080"