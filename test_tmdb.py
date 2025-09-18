import os, requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)
t = (os.getenv("TMDB_BEARER") or "").strip()
print("Token loaded:", bool(t), "length:", len(t))

r = requests.get(
    "https://api.themoviedb.org/3/search/movie",
    headers={"Authorization": f"Bearer {t}", "accept": "application/json"},
    params={"query": "Inception"},
    timeout=15
)
print("Status:", r.status_code)
print(r.text[:300])
