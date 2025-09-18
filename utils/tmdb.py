import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# --- Load API key from .env ---
ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ROOT_ENV, override=True)

TMDB_API_KEY = (os.getenv("TMDB_API_KEY") or "").strip()
if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY missing in .env")

BASE = "https://api.themoviedb.org/3"
HEADERS = {"accept": "application/json"}

# --- Core GET helper ---
def _get(path: str, params: dict | None = None) -> dict:
    try:
        params = dict(params or {})
        params["api_key"] = TMDB_API_KEY  # v3 key only
        resp = requests.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        # Fail gracefully, so Streamlit shows a message instead of crashing
        return {"error": str(e)}

# --- TMDB endpoints ---
def search_movies(query: str, page: int = 1) -> dict:
    return _get("/search/movie", {"query": query, "include_adult": False, "page": page})

def movie_details(movie_id: int) -> dict:
    return _get(f"/movie/{movie_id}", {"append_to_response": "credits,images,videos"})

def watch_providers(movie_id: int) -> dict:
    return _get(f"/movie/{movie_id}/watch/providers")

def similar_movies(movie_id: int, page: int = 1) -> dict:
    return _get(f"/movie/{movie_id}/similar", {"page": page})

def trending_movies(window: str = "day", page: int = 1) -> dict:
    """Trending can be 'day' or 'week'."""
    return _get(f"/trending/movie/{window}", {"page": page})

def top_rated_movies(page: int = 1) -> dict:
    return _get("/movie/top_rated", {"page": page})

# --- Helpers ---
def image_url(path: str | None, size: str = "w342") -> str:
    """Return full TMDB image URL, or a placeholder if missing."""
    if not path:
        return "https://via.placeholder.com/342x513.png?text=No+Image"
    return f"https://image.tmdb.org/t/p/{size}{path}"
