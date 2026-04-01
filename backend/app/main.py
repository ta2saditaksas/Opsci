from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # autorise tout (dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_TOKEN = os.getenv("TMDB_TOKEN")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


@app.get("/")
def root():
    return {"message": "Backend OK"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/movies")
def get_movies():
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant dans .env")

    url = f"{TMDB_BASE_URL}/movie/popular"
    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }
    params = {
        "language": "fr-FR",
        "page": 1
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur TMDB : {response.text}"
        )

    data = response.json()
    results = data.get("results", [])

    movies = []
    for movie in results:
        movies.append({
            "id": movie.get("id"),
            "title": movie.get("title"),
            "overview": movie.get("overview"),
            "release_date": movie.get("release_date"),
            "poster_url": f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie.get("poster_path") else None
        })

    return movies

@app.get("/search")
def search_movies(q: str):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant dans .env")

    url = f"{TMDB_BASE_URL}/search/movie"
    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }
    params = {
        "language": "fr-FR",
        "query": q,
        "page": 1
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Erreur TMDB : {response.text}"
        )

    data = response.json()
    results = data.get("results", [])

    movies = []
    for movie in results:
        movies.append({
            "id": movie.get("id"),
            "title": movie.get("title"),
            "overview": movie.get("overview"),
            "release_date": movie.get("release_date"),
            "poster_url": f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie.get("poster_path") else None
        })

    return movies
