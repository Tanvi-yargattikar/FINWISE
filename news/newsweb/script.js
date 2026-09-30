const API_KEY = "05abeb0fce2248a1a92c119913d5e6d1";
const BASE_URL = "https://newsapi.org/v2/everything?";
let currentPage = 1; // Track pages for infinite scrolling
let currentCategory = "finance"; // Default category

// 🌍 Load default news (Finance by default)
window.addEventListener("load", () => fetchNews(currentCategory));

// 📡 Fetch News with Pagination
async function fetchNews(category) {
    try {
        let query = `${category} AND (India OR NSE OR BSE OR Sensex OR Nifty OR RBI)`;
        let url = `${BASE_URL}q=${encodeURIComponent(query)}&sortBy=publishedAt&language=en&pageSize=20&page=${currentPage}&apiKey=${API_KEY}`;

        const res = await fetch(url);
        const data = await res.json();

        console.log("API Response:", data); // ✅ Debugging API Response

        if (data.status !== "ok") {
            console.error("API Error:", data.message);
            document.getElementById("cards-container").innerHTML =
                "<p style='color:white;'>Failed to fetch news. Try again later.</p>";
            return;
        }

        bindData(data.articles);
    } catch (error) {

        console.error("Error fetching news:", url);
    }
}

// 📌 Attach articles to UI dynamically
function bindData(articles) {
    console.log("Articles received:", articles); // ✅ Check if articles are loaded

    const cardsContainer = document.getElementById("cards-container");
    const newsCardTemplate = document.getElementById("template-news-card");

    if (!articles || articles.length === 0) {
        cardsContainer.innerHTML =
            "<p style='color:white;'>No articles found for this category.</p>";
        return;
    }

    articles.forEach(article => {
        if (!article.urlToImage) return;
        const cardClone = newsCardTemplate.content.cloneNode(true);
        fillDataInCard(cardClone, article);
        cardsContainer.appendChild(cardClone);
    });

    currentPage++; // Increment page for next load
}

// 🔗 Fill News Card Data
function fillDataInCard(cardClone, article) {
    const newsImg = cardClone.querySelector("#news-img");
    const newsTitle = cardClone.querySelector("#news-title");
    const newsSource = cardClone.querySelector("#news-source");
    const newsDesc = cardClone.querySelector("#news-desc");

    newsImg.src = article.urlToImage || "https://via.placeholder.com/400x200";
    newsTitle.innerHTML = article.title;
    newsDesc.innerHTML = article.description || "No description available.";

    const date = new Date(article.publishedAt).toLocaleString("en-US", {
        timeZone: "Asia/Kolkata",
    });

    newsSource.innerHTML = `${article.source.name} · ${date}`;

    cardClone.firstElementChild.addEventListener("click", () => {
        window.open(article.url, "_blank");
    });
}

// 🎯 Handle Navbar Category Click
let curSelectedNav = null;
function onNavItemClick(category) {
    currentCategory = category; // Set current category
    currentPage = 1; // Reset page for new category
    document.getElementById("cards-container").innerHTML = ""; // Clear old news
    fetchNews(category);

    const navItem = document.getElementById(category);
    curSelectedNav?.classList.remove("active");
    curSelectedNav = navItem;
    curSelectedNav.classList.add("active");
}

// 🔍 Handle User Search
const searchButton = document.getElementById("search-button");
const searchText = document.getElementById("search-text");

searchButton.addEventListener("click", () => {
    const query = searchText.value.trim();
    if (!query) return;

    currentPage = 1; // Reset page count when searching
    document.getElementById("cards-container").innerHTML = ""; // Clear old results
    fetchNews(query);

    curSelectedNav?.classList.remove("active");
    curSelectedNav = null; // Disable category selection when searching
});

// 🔄 Infinite Scroll: Load More News Dynamically
window.addEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
        fetchNews(currentCategory); // Load more news when scrolling down
    }
});