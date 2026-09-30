// script.js

const API_KEY = "YOUR_NEWSAPI_KEY";  // Get it from newsapi.org
const url = "https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=" + API_KEY;

window.addEventListener('load', () => fetchNews("finance"));

function fetchNews(query) {
    fetch(`${url}&q=${query}`)
        .then(response => response.json())
        .then(data => {
            bindData(data.articles);
        })
        .catch(error => {
            console.error("Error fetching news:", error);
        });
}

function bindData(articles) {
    const cardsContainer = document.getElementById("cards-container");
    const newsCardTemplate = document.getElementById("template-news-card");

    cardsContainer.innerHTML = "";

    articles.forEach(article => {
        if (!article.urlToImage) return;

        const cardClone = newsCardTemplate.content.cloneNode(true);
        fillDataInCard(cardClone, article);
        cardsContainer.appendChild(cardClone);
    });
}

function fillDataInCard(cardClone, article) {
    cardClone.querySelector("#news-img").src = article.urlToImage;
    cardClone.querySelector("#news-title").textContent = article.title;
    cardClone.querySelector("#news-source").textContent = `${article.source.name} • ${new Date(article.publishedAt).toLocaleDateString()}`;
    cardClone.querySelector("#news-desc").textContent = article.description;

    cardClone.querySelector(".card").addEventListener("click", () => {
        window.open(article.url, "_blank");
    });
}

document.getElementById("search-button").addEventListener("click", () => {
    const query = document.getElementById("search-text").value;
    if (!query) return;
    fetchNews(query);
});

function onNavItemClick(id) {
    fetchNews(id);
}
