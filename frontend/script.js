const API_URL = "http://127.0.0.1:8000/movies";
const container = document.getElementById("movies");

async function loadMovies() {
  try {
    const response = await fetch(API_URL);

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

  movies.forEach((movie) => {
    const card = document.createElement("article");
    card.className = "card";

    card.innerHTML = `
      <img src="${movie.poster_url || ''}" alt="${movie.title}">
      <div class="card-content">
        <h2>${movie.title}</h2>
        <p class="meta"><strong>Date :</strong> ${movie.release_date || "N/A"}</p>
        <p class="desc">${movie.overview || "Pas de description disponible."}</p>
      </div>
    `;

    container.appendChild(card);
  });
}

loadMovies();