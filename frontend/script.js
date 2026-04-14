//const API_URL = "http://127.0.0.1:8000/movies";
//const API_BASE = "http://127.0.0.1:8000"; on les met dans config.js

const MOVIES_URL = `${API_BASE}/movies`;
const container = document.getElementById("movies");
const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const resetButton = document.getElementById("resetButton");
const favoritesTitle = document.getElementById("favoritesTitle");
const favoritesContainer = document.getElementById("favorites");
const favoritesPageBtn = document.getElementById("favoritesPageBtn");
const recoPageBtn = document.getElementById("recoPageBtn");
const recoTitle = document.getElementById("recoTitle");
const recoContainer = document.getElementById("recommendations");
const homeBtn = document.getElementById("homeBtn");
let favoriteIds = [];

// Cacher au démarrage
favoritesContainer.style.display = "none";
favoritesTitle.style.display = "none";
recoContainer.style.display = "none";
recoTitle.style.display = "none";
homeBtn.style.display = "none";
favoritesPageBtn.style.display = "inline-block";
recoPageBtn.style.display = "inline-block";

// Filtre par humeur
document.querySelectorAll(".mood-tag").forEach(tag => {
  tag.addEventListener("click", () => {
    document.querySelectorAll(".mood-tag").forEach(t => t.classList.remove("active"));
    tag.classList.add("active");
    const mood = tag.dataset.mood;
    showOnly("home");
    loadMovies(`${API_BASE}/movies/mood/${mood}`);
  });
});

function showOnly(section) {
  container.style.display = "none";
  favoritesContainer.style.display = "none";
  favoritesTitle.style.display = "none";
  recoContainer.style.display = "none";
  recoTitle.style.display = "none";
  homeBtn.style.display = "inline-block";
  favoritesPageBtn.style.display = "inline-block";
  recoPageBtn.style.display = "inline-block";

  if (section === "home") {
    container.style.display = "grid";
    homeBtn.style.display = "none";
  } else if (section === "favorites") {
    favoritesContainer.style.display = "grid";
    favoritesTitle.style.display = "block";
    favoritesPageBtn.style.display = "none";
  } else if (section === "reco") {
    recoContainer.style.display = "grid";
    recoTitle.style.display = "block";
    recoPageBtn.style.display = "none";
  }
}

favoritesPageBtn.addEventListener("click", () => {
  showOnly("favorites");
  loadFavorites();
});

recoPageBtn.addEventListener("click", () => {
  showOnly("reco");
  loadRecommendationsFromFavorites();
});

homeBtn.addEventListener("click", () => {
  showOnly("home");
  loadMovies();
});

async function loadMovies(url = MOVIES_URL) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
    const movies = await response.json();
    renderMovies(movies);
  } catch (error) {
    container.innerHTML = `<p>Erreur lors du chargement des films : ${error.message}</p>`;
    console.error(error);
  }
}

function renderMovies(movies) {
  container.innerHTML = "";
  if (movies.length === 0) {
    container.innerHTML = `<p>Aucun film trouvé.</p>`;
    return;
  }

  movies.forEach((movie) => {
    const card = document.createElement("article");
    card.className = "card";
    card.innerHTML = `
      <img src="${movie.poster_url || ""}" alt="${movie.title}">
      <div class="overlay">
        <h3>${movie.title}</h3>
        <p>${movie.overview || "Pas de description disponible."}</p>
      </div>
      <div class="card-content">
        <h2>${movie.title}</h2>
        <p class="meta"><strong>Date :</strong> ${movie.release_date || "N/A"}</p>
        <p class="rating">⭐ ${movie.vote_average ? movie.vote_average.toFixed(1) + "/10" : "N/A"}</p>
        <button class="favorite-btn">
          ${favoriteIds.includes(movie.id) ? "Déjà en favori" : "Ajouter aux favoris"}
        </button>
        <button class="trailer-btn">▶ Bande annonce</button>
      </div>
    `;

    const favoriteButton = card.querySelector(".favorite-btn");
    favoriteButton.addEventListener("click", async () => {
      try {
        const response = await fetch(`${API_BASE}/favorites`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            movie_id: movie.id,
            title: movie.title,
            poster_url: movie.poster_url || ""
          })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Erreur ajout favoris");
        alert("Film ajouté aux favoris !");
        loadFavorites();
      } catch (error) {
        console.error(error);
        alert("Impossible d'ajouter le film aux favoris.");
      }
    });

    const trailerButton = card.querySelector(".trailer-btn");
    trailerButton.addEventListener("click", async () => {
      try {
        const response = await fetch(`${API_BASE}/movies/${movie.id}/trailer`);
        const data = await response.json();

        if (!data.trailer_url) {
          alert("Aucune bande annonce disponible.");
          return;
        }

        const modal = document.createElement("div");
        modal.className = "modal";
        modal.innerHTML = `
          <div class="modal-content">
            <button class="modal-close">✕</button>
            <iframe width="100%" height="400" src="${data.trailer_url}"
              frameborder="0" allowfullscreen></iframe>
          </div>
        `;
        document.body.appendChild(modal);

        modal.querySelector(".modal-close").addEventListener("click", () => {
          document.body.removeChild(modal);
        });

        modal.addEventListener("click", (e) => {
          if (e.target === modal) document.body.removeChild(modal);
        });

      } catch (error) {
        console.error(error);
        alert("Erreur lors du chargement de la bande annonce.");
      }
    });

    container.appendChild(card);
  });
}

searchButton.addEventListener("click", () => {
  const query = searchInput.value.trim();
  if (query) loadMovies(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
});

resetButton.addEventListener("click", () => {
  searchInput.value = "";
  loadMovies();
});

searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") searchButton.click();
});

let searchTimeout;
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimeout);
  const query = searchInput.value.trim();
  
  if (query.length === 0) {
    loadMovies();
    return;
  }
  
  if (query.length < 2) return;

  searchTimeout = setTimeout(() => {
    showOnly("home");
    loadMovies(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  }, 400);
});

async function loadFavorites() {
  try {
    const response = await fetch(`${API_BASE}/favorites`);
    const favorites = await response.json();
    favoriteIds = favorites.map(movie => movie.movie_id);
    favoritesContainer.innerHTML = "";

    if (favorites.length === 0) {
      favoritesContainer.innerHTML = "<p style='text-align:center;'>Aucun favori</p>";
      return;
    }

    favorites.forEach((movie) => {
      const card = document.createElement("article");
      card.className = "card";
      card.innerHTML = `
        <img src="${movie.poster_url || ""}" alt="${movie.title}">
        <div class="card-content">
          <h2>${movie.title}</h2>
          <button class="delete-btn">Supprimer</button>
        </div>
      `;
      const deleteButton = card.querySelector(".delete-btn");
      deleteButton.addEventListener("click", async () => {
        try {
          const response = await fetch(`${API_BASE}/favorites/${movie.movie_id}`, {
            method: "DELETE"
          });
          const data = await response.json();
          if (!response.ok) throw new Error(data.error || "Erreur suppression");
          alert("Film supprimé");
          loadFavorites();
          loadMovies();
        } catch (error) {
          console.error(error);
          alert("Impossible de supprimer.");
        }
      });
      favoritesContainer.appendChild(card);
    });
  } catch (error) {
    console.error(error);
  }
}

async function loadRecommendationsFromFavorites() {
  recoContainer.innerHTML = "<p>Chargement des recommandations...</p>";

  try {
    const response = await fetch(`${API_BASE}/favorites`);
    const favorites = await response.json();

    if (favorites.length === 0) {
      recoContainer.innerHTML = "<p style='text-align:center;'>Ajoutez des films en favoris pour obtenir des recommandations !</p>";
      return;
    }

    recoContainer.innerHTML = "";
    const seen = new Set();

    for (const fav of favorites) {
      const recoResponse = await fetch(`${API_BASE}/recommendations/${fav.movie_id}`);
      const recos = await recoResponse.json();

      recos.forEach((movie) => {
        if (seen.has(movie.id)) return;
        seen.add(movie.id);

        const card = document.createElement("article");
        card.className = "card";
        card.innerHTML = `
          <img src="${movie.poster_url || ""}" alt="${movie.title}">
          <div class="card-content">
            <h2>${movie.title}</h2>
            <p class="meta"><strong>Date :</strong> ${movie.release_date || "N/A"}</p>
            <p class="desc">${movie.overview || "Pas de description disponible."}</p>
          </div>
        `;
        recoContainer.appendChild(card);
      });
    }

    if (recoContainer.children.length === 0) {
      recoContainer.innerHTML = "<p style='text-align:center;'>Aucune recommandation trouvée.</p>";
    }

  } catch (error) {
    console.error(error);
    recoContainer.innerHTML = "<p>Erreur lors du chargement des recommandations.</p>";
  }
}

async function loadGenres() {
  try {
    const response = await fetch(`${API_BASE}/genres`);
    const genres = await response.json();

    const sidebar = document.querySelector(".sidebar");

    const genreSection = document.createElement("div");
    genreSection.innerHTML = `<h3>Genres</h3>`;

    const genreList = document.createElement("ul");
    genreList.className = "mood-list";

    genres.forEach(genre => {
      const li = document.createElement("li");
      li.className = "mood-tag";
      li.textContent = genre.name;
      li.addEventListener("click", () => {
        document.querySelectorAll(".mood-tag").forEach(t => t.classList.remove("active"));
        li.classList.add("active");
        showOnly("home");
        loadMovies(`${API_BASE}/movies/genre/${genre.id}`);
      });
      genreList.appendChild(li);
    });

    genreSection.appendChild(genreList);
    sidebar.appendChild(genreSection);
  } catch (error) {
    console.error("Erreur genres:", error);
  }
}

async function init() {
  await loadFavorites();
  await loadMovies();
  await loadGenres();
}

init();