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
const homeBtn = document.getElementById("homeBtn");
let favoriteIds = [] ;

favoritesPageBtn.addEventListener("click", () => {
  container.style.display = "none"; // cacher films
  favoritesContainer.style.display = "grid"; // afficher favoris
  favoritesTitle.style.display = "block";
  loadFavorites();
  
  homeBtn.style.display = "inline-block"; // afficher bouton accueil
});

homeBtn.addEventListener("click", () => {
  container.style.display = "grid"; // afficher films
  favoritesContainer.style.display = "none"; // cacher favoris
  favoritesTitle.style.display = "none";
  loadMovies();

  homeBtn.style.display = "none"; // cacher bouton accueil
});

//les cacher au démarrge
favoritesContainer.style.display = "none";
homeBtn.style.display = "none";
favoritesTitle.style.display = "none";


async function loadMovies(url = MOVIES_URL) {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Erreur HTTP : ${response.status}`);
    }

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
      <div class="card-content">
        <h2>${movie.title}</h2>
        <p class="meta"><strong>Date :</strong> ${movie.release_date || "N/A"}</p>
        <p class="desc">${movie.overview || "Pas de description disponible."}</p>
        <button class="favorite-btn">
          ${favoriteIds.includes(movie.id) ? "Déjà en favori" : "Ajouter aux favoris"}
        </button>
      </div>
    `;

    const favoriteButton = card.querySelector(".favorite-btn");

favoriteButton.addEventListener("click", async () => {
  try {
    const response = await fetch(`${API_BASE}/favorites`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        movie_id: movie.id,
        title: movie.title,
        poster_url: movie.poster_url || ""
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Erreur lors de l'ajout aux favoris");
    }

    alert("Film ajouté aux favoris ");
    loadFavorites();
      } catch (error) {
        console.error(error);
    alert("Impossible d'ajouter le film aux favoris.");
      }
    });

    container.appendChild(card);
    loadRecommendations(movie.id, card);

  });
}

searchButton.addEventListener("click", () => {
  const query = searchInput.value.trim();
  if (query) {
    loadMovies(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  }
});

resetButton.addEventListener("click", () => {
  searchInput.value = "";
  loadMovies();
});

searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    searchButton.click();
  }
});



async function loadFavorites() {
  try {
    const response = await fetch(`${API_BASE}/favorites`);
    const favorites = await response.json();
    favoriteIds = favorites.map(movie => movie.movie_id) ;

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

          if (!response.ok) {
            throw new Error(data.error || "Erreur suppression");
          }

          alert("Film supprimé");
          loadFavorites();
          loadMovies(); // pour mettre à jour les boutons 
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

async function init() {
  await loadFavorites();
  await loadMovies();
}

init();

async function loadRecommendations(movieId, container) {
  try {
    const response = await fetch(`${API_BASE}/recommendations/${movieId}`);
    const recommendations = await response.json();

    if (recommendations.length === 0) return;

    const recoDiv = document.createElement("div");
    recoDiv.className = "recommendations";
    recoDiv.innerHTML = `<p><strong>Films similaires :</strong></p>`;

    recommendations.forEach((movie) => {
      const span = document.createElement("span");
      span.textContent = movie.title;
      span.className = "reco-tag";
      span.addEventListener("click", () => {
        loadMovies(`${API_BASE}/search?q=${encodeURIComponent(movie.title)}`);
        window.scrollTo(0, 0);
      });
      recoDiv.appendChild(span);
    });

    container.appendChild(recoDiv);
  } catch (error) {
    console.error("Erreur recommandations:", error);
  }
}