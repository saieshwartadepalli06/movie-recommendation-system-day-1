document.addEventListener('DOMContentLoaded', () => {
    // Close modal functionality
    const modal = document.getElementById('movie-info-modal');
    const span = document.getElementsByClassName('close')[0];
    span.onclick = () => modal.style.display = 'none';
    window.onclick = event => {
        if (event.target === modal) modal.style.display = 'none';
    };

    // Attach event listeners to movie items for modal and recommendations
    attachEventListeners();
});

function attachEventListeners() {
    // Show movie info in modal when title is clicked
    document.querySelectorAll('.movie-item h2').forEach(titleElement => {
        titleElement.addEventListener('click', function() {
            const movieDataStr = this.getAttribute('data-movie');
            showMovieInfoModal(movieDataStr);
        });
    });
    
    // document.querySelectorAll('.movie-item h2').forEach(element => {
    //     element.addEventListener('click', () => {
    //         const movieDataStr = element.getAttribute('data-movie');
    //         showMovieInfoModal(movieDataStr);
    //     });
    // });

    // Fetch more recommendations when image is clicked
    document.querySelectorAll('.movie-item img').forEach(img => {
        img.addEventListener('click', () => {
            const title = img.getAttribute('alt');
            getMoreRecommendations(title);
        });
    });
}

function showMovieInfoModal(movieDataStr) {
    const movie = JSON.parse(movieDataStr); // Ensure you're parsing the JSON string to an object
    const modal = document.getElementById('movie-info-modal');
    const info = document.getElementById('movie-info');
    const infoHtml = `
        <h2>${movie.Title}</h2>
        <p><b>Stars:</b> ${movie.Star_1}, ${movie.Star_2}, ${movie.Star_3}, ${movie.Star_4}</p>
        <p><b>Director:</b> ${movie.Director_Name}</p>
        <p><b>IMDb Rating:</b> ${movie['IMDb Rating']}</p>
        <p><b>Genres:</b> ${movie.Genre_1}, ${movie.Genre_2}, ${movie.Genre_3}</p>
    `;
    info.innerHTML = infoHtml;
    modal.style.display = 'block';
}


// function showMovieInfoModal(movieDataStr) {
//     const movie = JSON.parse(movieDataStr);
//     const modal = document.getElementById('movie-info-modal');
//     const info = document.getElementById('movie-info');
    
//     // Ensure properties match those in your dataset
//     const infoHtml = `
//         <h2>${movie.Title}</h2>
//         <p><b>Stars:</b> ${movie.Stars}</p>
//         <p><b>Director:</b> ${movie.Director}</p>
//         <p><b>IMDb Rating:</b> ${movie.IMDb_Rating}</p>
//         <p><b>Genres:</b> ${movie.Genres}</p>
//     `;

//     info.innerHTML = infoHtml;
//     modal.style.display = 'block';
// }


function getMoreRecommendations(title) {
    fetch(`/get-recommendations?title=${encodeURIComponent(title)}`)
        .then(response => response.ok ? response.json() : Promise.reject('Failed to load'))
        .then(updateMovieGrid)
        .catch(error => console.error('Error:', error));
}

function updateMovieGrid(movies) {
    const grid = document.querySelector('.movie-grid');
    grid.innerHTML = ''; // Clear current movies
    movies.forEach(movie => {
        const movieEl = document.createElement('div');
        movieEl.className = 'movie-item';
        movieEl.innerHTML = `
            <img class="movie-image" src="${movie.imageURL}" alt="${movie.Title}" data-movie='${JSON.stringify(movie)}'>
            <h2 data-movie='${JSON.stringify(movie)}'>${movie.Title}</h2>`;
        grid.appendChild(movieEl);
    });
    // Reattach event listeners for new movie items
    attachEventListeners();
}
