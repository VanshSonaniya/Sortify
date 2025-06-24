import requests
import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_youtube_videos(query="technology", max_results=4):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={query}&maxResults={max_results}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items", [])
        return [
            {
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "video_id": item["id"]["videoId"]
            } for item in items
        ]
    return []

def fetch_news_articles(query="technology", page_size=4):
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&pageSize={page_size}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [
            {
                "title": article["title"],
                "description": article["description"],
                "url": article["url"]
            } for article in articles
        ]
    return []