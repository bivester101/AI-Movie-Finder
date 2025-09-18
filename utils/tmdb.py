# utils/tmdb.py
import os
import requests
from pathlib import Path

# Try dotenv locally
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

# Try Streamlit secrets if running on Streamlit Cloud
try:
    import streamlit as st
    TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "")
except Exception:
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()

if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY missing! Add it to .env locally or st.secrets in Streamlit Cloud.")

BASE = "https://api.themoviedb.org/3"
HEADERS = {"accept": "application/json"}

def _get(path: str, params: dict | None = None) -> dict:
    params = dict(params or {})
    params["api_key"] = TMDB_API_KEY
    resp = requests.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

def search_movies(query: str, page: int = 1) -> dict:
    return _get("/search/movie", {"query": query, "include_adult": False, "page": page})

def movie_details(movie_id: int) -> dict:
    return _get(f"/movie/{movie_id}", {"append_to_response": "credits,images,videos"})

def watch_providers(movie_id: int) -> dict:
    return _get(f"/movie/{movie_id}/watch/providers")

def similar_movies(movie_id: int, page: int = 1) -> dict:
    return _get(f"/movie/{movie_id}/similar", {"page": page})

def trending_movies(window: str = "day") -> dict:
    return _get(f"/trending/movie/{window}")

def top_rated_movies(page: int = 1) -> dict:
    return _get("/movie/top_rated", {"page": page})

def image_url(path: str | None, size: str = "w342") -> str | None:
    if not path:
        return None
    return f"https://image.tmdb.org/t/p/{size}{path}"

