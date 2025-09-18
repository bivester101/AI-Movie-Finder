# 🎬 AI Movie Finder

A modern Streamlit app that lets you:
- 🔍 Search movies using **The Movie Database (TMDB)**
- 📺 See **where to watch** (JustWatch data via TMDB’s providers API)
- ❤️ Save titles to **My List** (SQLite persistence)
- 🔥 Browse **Trending** and **Top Rated**
- 🎨 Netflix-inspired UI + dark theme

> Live demo: **(link will go here after you deploy)**  
> Repo: https://github.com/bivester101/AI-Movie-Finder

---

## ✨ Features

- **Fast search** with caching
- **Detail pages**: overview, genres, runtime, rating, poster, similar movies
- **Where to watch** by region (US, MX, GB, CA, DE, FR, JP)
- **My List** (favorites) stored locally in `data/app.db`
- **Auto-seed** favorites (Inception, Matrix, Interstellar, The Dark Knight) on first run
- **Responsive grid** layout and clean styling

---

## 🧱 Tech Stack

- Python 3.10+  
- [Streamlit](https://streamlit.io/)  
- [TMDB API](https://www.themoviedb.org/documentation/api)  
- SQLite (via `sqlite3`)  
- `requests`, `python-dotenv`

---

## 📁 Project Structure

