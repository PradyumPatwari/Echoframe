const newsFeed = document.getElementById("news-feed");

// Your NewsAPI key
const apiKey = "qau8tr2tihhjewhomnjxjejfncouc5qz8lleut6x";

// API endpoint (you can adjust query & country)
const url = `https://newsapi.org/v2/everything?q=deepfake+scam+fraud&language=en&sortBy=publishedAt&apiKey=${apiKey}`;

async function loadNews() {
  try {
    newsFeed.innerHTML = "<p>Fetching latest scam alerts...</p>";
    
    const response = await fetch(url);
    const data = await response.json();

    // Clear old content
    newsFeed.innerHTML = "";

    if (data.articles && data.articles.length > 0) {
      data.articles.slice(0, 5).forEach(article => {
        const div = document.createElement("div");
        div.classList.add("news-item");
        div.innerHTML = `
          <h4><a href="${article.url}" target="_blank">${article.title}</a></h4>
          <p>${article.description || ""}</p>
          <small>🕒 ${new Date(article.publishedAt).toLocaleString()}</small>
        `;
        newsFeed.appendChild(div);
      });
    } else {
      newsFeed.innerHTML = "<p>No recent scam news found.</p>";
    }
  } catch (error) {
    console.error("Error fetching news:", error);
    newsFeed.innerHTML = "<p>⚠️ Unable to load news at the moment.</p>";
  }
}

// Load immediately and refresh every 10 minutes
loadNews();
setInterval(loadNews, 600000); // 600,000 ms = 10 minutes
