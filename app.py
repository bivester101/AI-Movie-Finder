import streamlit as st

from utils.tmdb import (
    search_movies, movie_details, watch_providers, similar_movies, image_url,
    trending_movies, top_rated_movies
)
from utils.db import fav_count, add_fav, list_favs, remove_fav, is_fav

# --- Seed "My List" on first run (only if empty) ---
def _seed_my_list_if_empty():
    try:
        if fav_count() > 0:
            return  # already seeded / has data

        # Some popular TMDB movies by ID
        seed_ids = [27205, 603, 157336, 155]   # Inception, The Matrix, Interstellar, The Dark Knight
        for mid in seed_ids:
            det = movie_details(mid)
            if not det:
                continue
            title = det.get("title", "")
            poster = image_url(det.get("poster_path"))
            year = (det.get("release_date") or "")[:4]
            add_fav(mid, title, poster, year)
    except Exception:
        # ignore seed errors so the app still runs
        pass

_seed_my_list_if_empty()

# ---------- Page setup ----------
st.set_page_config(page_title="AI Movie Finder", page_icon="🎬", layout="wide")
st.title("🎬 AI Movie Finder")

# Safe, neutral CSS
st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px; }
.card { background:#1f1f1f; border-radius:16px; padding:10px; transition:transform .15s ease, box-shadow .15s ease; }
.card:hover { transform:translateY(-3px); box-shadow:0 10px 24px rgba(0,0,0,.35); }
.card-title { font-weight:600; margin-top:.4rem; font-size:.95rem; }
.badge { display:inline-block; padding:.15rem .55rem; border-radius:999px; background:#2b2b2b; margin:.2rem .25rem 0 0; font-size:.75rem; }
.provider { display:inline-block; padding:.25rem .6rem; border-radius:10px; background:#2b2b2b; margin:.2rem .25rem 0 0; font-size:.82rem; }
.poster-skel { width:100%; aspect-ratio:2/3; border-radius:12px;
  background:linear-gradient(135deg,#2a2a2a,#202020);
  display:flex; align-items:center; justify-content:center; color:#8a8a8a; font-size:.9rem; border:1px solid #333; }
.row-title { font-size:1.1rem; font-weight:700; margin: 0.75rem 0 0.25rem 0; }
.sidebar-item { display:flex; gap:.6rem; align-items:center; margin:.35rem 0; }
.sidebar-item img { width:28px; height:42px; border-radius:6px; object-fit:cover; border:1px solid #333; }
.sidebar-title { font-size:.86rem; line-height:1.1rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar: My List ----------
with st.sidebar:
    st.subheader("❤️ My List")
    favs = list_favs()
    if not favs:
        st.caption("No favorites yet.")
    else:
        for mid, title, poster, year in favs:
            c1, c2, c3 = st.columns([1, 4, 1])
            with c1:
                if poster:
                    st.image(poster, use_container_width=True)
            with c2:
                st.caption(f"{title} {f'({year})' if year else ''}")
                if st.button("Open", key=f"open_fav_{mid}", use_container_width=True):
                    st.session_state.selected_movie_id = mid
                    st.rerun()
            with c3:
                if st.button("✕", key=f"rm_fav_{mid}"):
                    remove_fav(mid)
                    st.rerun()

# ---------- Controls ----------
region = st.selectbox(
    "Choose region for streaming availability:",
    ["US", "MX", "GB", "CA", "DE", "FR", "JP"],
    index=0,
)
qcol1, qcol2 = st.columns([5,1])
with qcol1:
    query = st.text_input("Search for a movie", placeholder="e.g., Inception", key="search_q")
with qcol2:
    if st.button("Clear", use_container_width=True):
        st.session_state.search_q = ""
        st.session_state.selected_movie_id = None
        st.rerun()

# ---------- Session state ----------
if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# Reset opened movie when the query text changes
if st.session_state.search_q != st.session_state.last_query:
    st.session_state.selected_movie_id = None
    st.session_state.last_query = st.session_state.search_q

# ---------- Cached wrappers ----------
@st.cache_data(ttl=1800)
def _cached_search(q): 
    return search_movies(q)

@st.cache_data(ttl=1800)
def _cached_details(mid): 
    return movie_details(mid)

@st.cache_data(ttl=1800)
def _cached_providers(mid): 
    return watch_providers(mid)

@st.cache_data(ttl=1800)
def _cached_similar(mid): 
    return similar_movies(mid)

@st.cache_data(ttl=1200)  # 20 min is fine for home rows
def _cached_trending(window="day"): 
    return trending_movies(window=window)

@st.cache_data(ttl=1200)
def _cached_top_rated(): 
    return top_rated_movies()

# ---------- Small UI helpers ----------
def poster_or_placeholder(url: str | None):
    if url:
        st.image(url, use_container_width=True)
    else:
        st.markdown("<div class='poster-skel'>No image</div>", unsafe_allow_html=True)

def render_grid(items, open_key_prefix, max_items=12):
    cols = st.columns(4, gap="large")
    for i, m in enumerate(items[:max_items]):
        with cols[i % 4]:
            with st.container(border=True):
                poster_or_placeholder(image_url(m.get("poster_path")))
                title = m.get("title", "Untitled")
                year = (m.get("release_date") or "")[:4]
                st.markdown(f"<div class='card-title'>{title} {f'({year})' if year else ''}</div>", unsafe_allow_html=True)
                if st.button("Open", key=f"{open_key_prefix}_{m['id']}", use_container_width=True):
                    st.session_state.selected_movie_id = m["id"]
                    st.rerun()

def render_row(title, items, key_prefix, max_items=10):
    st.markdown(f"<div class='row-title'>{title}</div>", unsafe_allow_html=True)
    cols = st.columns(5, gap="large")
    for i, m in enumerate(items[:max_items]):
        with cols[i % 5]:
            with st.container(border=True):
                poster_or_placeholder(image_url(m.get("poster_path"), "w342"))
                t = m.get("title","")
                st.caption(t)
                if st.button("Open", key=f"{key_prefix}_{m['id']}", use_container_width=True):
                    st.session_state.selected_movie_id = m["id"]
                    st.rerun()

# ---------- Main: search vs. home rows ----------
query = st.session_state.search_q.strip()
if query:
    # Search mode
    try:
        with st.spinner("Searching…"):
            data = _cached_search(query)
        if data.get("error"):
            st.error(f"Search error: {data['error']}")
        else:
            results = data.get("results", [])
            if not results:
                st.info("No results. Try another title or spelling.")
            else:
                st.subheader("Results")
                render_grid(results, open_key_prefix="open")
    except Exception as e:
        st.error(f"Search error: {e}")
else:
    # Home mode (no query): Trending & Top Rated rows
    try:
        colA, colB = st.columns(2)
        with colA:
            st.caption("Home")
        with colB:
            # Optional toggle to change trending window
            window = st.segmented_control("Trending window", options=["day", "week"], default="day", key="trend_window")
        with st.spinner("Loading home rows…"):
            tr = _cached_trending(st.session_state.trend_window or "day")
            top = _cached_top_rated()
        if tr.get("results"):
            render_row("🔥 Trending now", tr["results"], key_prefix="trend")
        if top.get("results"):
            render_row("⭐ Top rated", top["results"], key_prefix="top")
    except Exception as e:
        st.error(f"Home rows error: {e}")

# ---------- Detail view ----------
mid = st.session_state.selected_movie_id
if mid:
    try:
        with st.spinner("Loading details…"):
            det = _cached_details(mid)

        # If API wrapper returned an error, show it
        if det.get("error"):
            st.error(f"Details error: {det['error']}")
        else:
            st.header(det.get("title", "Movie"))
            tab1, tab2, tab3 = st.tabs(["Overview", "Where to watch", "You might also like"])

            # --- Overview ---
            with tab1:
                c1, c2 = st.columns([1, 2], gap="large")
                with c1:
                    poster_or_placeholder(image_url(det.get("poster_path"), "w500"))
                with c2:
                    st.markdown(
                        f"**Released:** {det.get('release_date', '—')}  \n"
                        f"**Runtime:** {det.get('runtime', '—')} min  \n"
                        f"**TMDB Rating:** {det.get('vote_average', '—')}/10"
                    )
                    if det.get("genres"):
                        st.markdown(
                            "".join(f"<span class='badge'>{g['name']}</span>" for g in det["genres"]),
                            unsafe_allow_html=True
                        )

                    # --- Favorites toggle ---
                    fav_now = is_fav(det["id"])
                    btn_label = "➖ Remove from My List" if fav_now else "➕ Add to My List"
                    if st.button(btn_label, key=f"fav_{det['id']}", use_container_width=True):
                        if fav_now:
                            remove_fav(det["id"])
                            st.toast("Removed from My List")
                        else:
                            add_fav(
                                det["id"],
                                det.get("title", ""),
                                image_url(det.get("poster_path")),
                                (det.get("release_date") or "")[:4],
                            )
                            st.toast("Added to My List")
                        st.rerun()

                    st.write(det.get("overview") or "No overview available.")

            # --- Where to watch ---
            with tab2:
                with st.spinner("Fetching providers…"):
                    prov_all = _cached_providers(mid).get("results", {})
                prov = prov_all.get(region, {})
                st.markdown(f"**Region:** {region}")
                if prov:
                    link = prov.get("link")
                    if link:
                        st.link_button("Open on JustWatch", link, use_container_width=True)
                    buckets = [
                        ("Included (subscription)", "flatrate"),
                        ("Free with ads", "ads"),
                        ("Free", "free"),
                        ("Rent", "rent"),
                        ("Buy", "buy"),
                    ]
                    for label, key in buckets:
                        items = prov.get(key)
                        if items:
                            st.markdown(
                                f"**{label}:** " +
                                "".join(f"<span class='provider'>{p.get('provider_name','')}</span>" for p in items),
                                unsafe_allow_html=True
                            )
                else:
                    st.info(f"No streaming info for {region}. Try a different region.")

            # --- Similar ---
            with tab3:
                with st.spinner("Finding similar titles…"):
                    sim = _cached_similar(mid).get("results", [])[:10]
                if sim:
                    render_grid(sim, open_key_prefix="sim", max_items=10)
                else:
                    st.caption("No similar titles found.")
    except Exception as e:
        st.error(f"Details error: {e}")
