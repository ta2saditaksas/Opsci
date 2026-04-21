from sqlalchemy import create_engine, text
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import requests
import redis
import json
import time

redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/movies_db"
)
engine = create_engine(DATABASE_URL)
for i in range(10):
    try:
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id SERIAL PRIMARY KEY,
                    movie_id INTEGER UNIQUE NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    poster_url TEXT
                )
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS history (
                    id SERIAL PRIMARY KEY,
                    movie_id INTEGER NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    poster_url TEXT,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            connection.commit()
        break
    except Exception:
        time.sleep(3)

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

def format_movie(movie):
    return {
        "id": movie.get("id"),
        "title": movie.get("title"),
        "overview": movie.get("overview"),
        "release_date": movie.get("release_date"),
        "vote_average": movie.get("vote_average"),
        "poster_url": f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie.get("poster_path") else None
    }

@app.get("/")
def root():
    return {"message": "Backend OK"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/movies")
def get_movies(page: int = 1):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant dans .env")

    cache_key = f"movies_popular_page_{page}"
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except:
        pass

    url = f"{TMDB_BASE_URL}/movie/popular"
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}
    params = {"language": "fr-FR", "page": page}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Erreur TMDB : {response.text}")

    movies = [format_movie(m) for m in response.json().get("results", [])]

    try:
        redis_client.setex(cache_key, 600, json.dumps(movies))
    except:
        pass

    return movies

@app.get("/search")
def search_movies(q: str):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant dans .env")

    url = f"{TMDB_BASE_URL}/search/movie"
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}
    params = {"language": "fr-FR", "query": q, "page": 1}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Erreur TMDB : {response.text}")

    return [format_movie(m) for m in response.json().get("results", [])]


@app.get("/test-db")
def test_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
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
            return [{"id": row.id, "movie_id": row.movie_id, "title": row.title, "poster_url": row.poster_url} for row in result]
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
                text("INSERT INTO favorites (movie_id, title, poster_url) VALUES (:movie_id, :title, :poster_url)"),
                {"movie_id": movie.movie_id, "title": movie.title, "poster_url": movie.poster_url}
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
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}
    params = {"language": "fr-FR", "page": 1}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Erreur TMDB : {response.text}")

    return [format_movie(m) for m in response.json().get("results", [])[:5]]


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
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}
    params = {"language": "fr-FR", "with_genres": genres, "sort_by": "popularity.desc", "page": 1}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Erreur TMDB : {response.text}")

    return [format_movie(m) for m in response.json().get("results", [])]

@app.get("/genres")
def get_genres():
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant")

    url = f"{TMDB_BASE_URL}/genre/movie/list"
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}
    params = {"language": "fr-FR"}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    return response.json().get("genres", [])


@app.get("/movies/genre/{genre_id}")
def get_movies_by_genre(genre_id: int):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant")

    url = f"{TMDB_BASE_URL}/discover/movie"
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}
    params = {"language": "fr-FR", "with_genres": genre_id, "sort_by": "popularity.desc", "page": 1}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    return [format_movie(m) for m in response.json().get("results", [])]


@app.get("/movies/{movie_id}/trailer")
def get_trailer(movie_id: int):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant")

    url = f"{TMDB_BASE_URL}/movie/{movie_id}/videos"
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}

    for lang in ["fr-FR", "en-US"]:
        response = requests.get(url, headers=headers, params={"language": lang}, timeout=10)
        for video in response.json().get("results", []):
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return {"trailer_url": f"https://www.youtube.com/embed/{video['key']}"}

    return {"trailer_url": None}

@app.get("/trending")
def get_trending():
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant")

    try:
        cached = redis_client.get("movies_trending")
        if cached:
            return json.loads(cached)
    except:
        pass

    url = f"{TMDB_BASE_URL}/trending/movie/day"
    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}
    params = {"language": "fr-FR"}

    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Erreur TMDB : {response.text}")

    movies = [format_movie(m) for m in response.json().get("results", [])]

    try:
        redis_client.setex("movies_trending", 600, json.dumps(movies))
    except:
        pass

    return movies

@app.get("/movies/{movie_id}/details")
def get_movie_details(movie_id: int):
    if not TMDB_TOKEN:
        raise HTTPException(status_code=500, detail="TMDB_TOKEN manquant")

    headers = {"Authorization": f"Bearer {TMDB_TOKEN}", "accept": "application/json"}

    # Infos du film
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {"language": "fr-FR", "append_to_response": "credits"}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Film non trouvé")

    data = response.json()

    # Casting (5 premiers acteurs)
    cast = []
    for member in data.get("credits", {}).get("cast", [])[:5]:
        cast.append({
            "name": member.get("name"),
            "character": member.get("character"),
            "profile_url": f"{TMDB_IMAGE_BASE_URL}{member['profile_path']}" if member.get("profile_path") else None
        })

    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "overview": data.get("overview"),
        "release_date": data.get("release_date"),
        "vote_average": data.get("vote_average"),
        "runtime": data.get("runtime"),
        "genres": [g["name"] for g in data.get("genres", [])],
        "poster_url": f"{TMDB_IMAGE_BASE_URL}{data['poster_path']}" if data.get("poster_path") else None,
        "backdrop_url": f"https://image.tmdb.org/t/p/original{data['backdrop_path']}" if data.get("backdrop_path") else None,
        "cast": cast
    }

class HistoryMovie(BaseModel):
    movie_id: int
    title: str
    poster_url: str | None = None

@app.post("/history")
def add_history(movie: HistoryMovie):
    try:
        with engine.connect() as connection:
            connection.execute(
                text("INSERT INTO history (movie_id, title, poster_url) VALUES (:movie_id, :title, :poster_url)"),
                {"movie_id": movie.movie_id, "title": movie.title, "poster_url": movie.poster_url}
            )
            connection.commit()
        return {"message": "Film ajouté à l'historique"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/history")
def get_history():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT DISTINCT ON (movie_id) id, movie_id, title, poster_url, viewed_at FROM history ORDER BY movie_id, viewed_at DESC")
            )
            return [{"id": row.id, "movie_id": row.movie_id, "title": row.title, "poster_url": row.poster_url, "viewed_at": str(row.viewed_at)} for row in result]
    except Exception as e:
        return {"error": str(e)}