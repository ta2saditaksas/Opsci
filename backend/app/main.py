from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import requests
import redis
import json

redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/movies_db"
)
engine = create_engine(DATABASE_URL)
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS favorites (
            id SERIAL PRIMARY KEY,
            movie_id INTEGER UNIQUE NOT NULL,
            title VARCHAR(255) NOT NULL,
            poster_url TEXT
        )
    """))
    connection.commit()

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

class FavoriteMovie(BaseModel):
    movie_id: int
    title: str
    poster_url: str | None = None

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

    # Vérifier le cache Redis
    try:
        cached = redis_client.get("movies_popular")
        if cached:
            return json.loads(cached)
    except:
        pass

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

    # Stocker dans Redis pendant 10 minutes
    try:
        redis_client.setex("movies_popular", 600, json.dumps(movies))
    except:
        pass

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


@app.get("/test-db")
def test_db():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {"message": "Connexion PostgreSQL OK"}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/favorites")
def get_favorites():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT id, movie_id, title, poster_url FROM favorites ORDER BY id DESC")
            )
            favorites = []
            for row in result:
                favorites.append({
                    "id": row.id,
                    "movie_id": row.movie_id,
                    "title": row.title,
                    "poster_url": row.poster_url
                })
            return favorites
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/favorites")
def add_favorite(movie: FavoriteMovie):
    try:
        with engine.connect() as connection:
            existing = connection.execute(
                text("SELECT id FROM favorites WHERE movie_id = :movie_id"),
                {"movie_id": movie.movie_id}
            ).fetchone()

            if existing:
                return {"message": "Film déjà présent dans les favoris"}

            connection.execute(
                text("""
                    INSERT INTO favorites (movie_id, title, poster_url)
                    VALUES (:movie_id, :title, :poster_url)
                """),
                {
                    "movie_id": movie.movie_id,
                    "title": movie.title,
                    "poster_url": movie.poster_url
                }
            )
            connection.commit()

        return {"message": "Film ajouté aux favoris"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/favorites/{movie_id}")
def delete_favorite(movie_id: int):
    try:
        with engine.connect() as connection:
            connection.execute(
                text("DELETE FROM favorites WHERE movie_id = :movie_id"),
                {"movie_id": movie_id}
            )
            connection.commit()

        return {"message": "Film supprimé des favoris"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/recommendations/{movie_id}")
def get_recommendations(movie_id: int):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant dans .env")

    url = f"{TMDB_BASE_URL}/movie/{movie_id}/similar"
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
    results = data.get("results", [])[:5]

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
MOOD_GENRES = {
    "bonne_humeur": [35, 16],      # Comédie, Animation
    "melancolique": [18, 10749],   # Drame, Romance
    "sensations": [27, 53],        # Horreur, Thriller
    "aventure": [28, 878],         # Action, Science-Fiction
    "reflechi": [99, 36]           # Documentaire, Histoire
}

@app.get("/movies/mood/{mood}")
def get_movies_by_mood(mood: str):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant")

    if mood not in MOOD_GENRES:
        raise HTTPException(status_code=404, detail="Humeur non reconnue")

    genres = ",".join(str(g) for g in MOOD_GENRES[mood])

    url = f"{TMDB_BASE_URL}/discover/movie"
    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }
    params = {
        "language": "fr-FR",
        "with_genres": genres,
        "sort_by": "popularity.desc",
        "page": 1
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Erreur TMDB : {response.text}")

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

@app.get("/genres")
def get_genres():
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant")

    url = f"{TMDB_BASE_URL}/genre/movie/list"
    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }
    params = {"language": "fr-FR"}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    data = response.json()
    return data.get("genres", [])


@app.get("/movies/genre/{genre_id}")
def get_movies_by_genre(genre_id: int):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant")

    url = f"{TMDB_BASE_URL}/discover/movie"
    headers = {
        "Authorization": f"Bearer {TMDB_TOKEN}",
        "accept": "application/json"
    }
    params = {
        "language": "fr-FR",
        "with_genres": genre_id,
        "sort_by": "popularity.desc",
        "page": 1
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)
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