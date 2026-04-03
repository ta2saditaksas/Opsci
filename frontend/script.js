const API_URL = "http://127.0.0.1:8000/movies";


const API_BASE = "http://127.0.0.1:8000";
const MOVIES_URL = `${API_BASE}/movies`;
const container = document.getElementById("movies");

const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const resetButton = document.getElementById("resetButton");

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
        <button class="favorite-btn"> Ajouter aux favoris</button>
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
      } catch (error) {
        console.error(error);
    alert("Impossible d'ajouter le film aux favoris.");
      }
    });

    container.appendChild(card);
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

loadMovies();
