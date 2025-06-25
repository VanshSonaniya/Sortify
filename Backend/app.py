from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from models.content_db import ContentDB
from models.user_db import User, UserDB  
from utils_api_fetch import fetch_youtube_videos, fetch_news_articles 
from dotenv import load_dotenv
import requests
import random
import os

# Loading .env which consists of all the API's and secret keys.
load_dotenv()

#Setting the path for the templates folder
template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../Frontend/templates')

# Initialize the Flask app with custom template folder path
app = Flask(__name__, template_folder=template_path)

#Load API Keys and Secret Key from .env
app.secret_key = os.getenv("SECRET_KEY")  
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


#----------------------------All The Rooutes of the Application---------------------------------------------------

#Login Route. It is the first page that the user will see. After running the webapp
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emailId = request.form.get("emailId")
        password = request.form.get("password")
        
        db = UserDB()
        user_data = db.validate_user(emailId, password)

        if user_data:
            session["emailId"] = emailId
            return redirect("/home")
        else:
            return render_template("login.html", error="❌ Invalid email or password. Please try again.")
    
    return render_template("login.html")


# Registration Route. It allows the user to register a new account.
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        emailId = request.form.get("emailId")
        password = request.form.get("password")
        name = request.form.get("name")

        if not emailId or not password or not name:
            error = " Please fill in all required fields."
            return render_template("register.html", error=error)

        user = User(emailId, password, name)
        db = UserDB()
        success = db.add_user(user)

        if success:
            return redirect("/")
        else:
            error = " This email is already registered. Please log in or use another."
            return render_template("register.html", error=error)

    return render_template("register.html")


# Home Route. It is the main page of the application after login. 
@app.route("/home")
def home():
    if "emailId" not in session:
        return redirect("/")
    videos = fetch_youtube_videos()
    blogs = fetch_news_articles()
    return render_template("home.html", videos=videos, blogs=blogs)


# This is the route for a category page which have some predefined limited categories. 
@app.route("/categories")
def categories():
    categories_list = [
        "Technology", "Sports", "Business and Finance", "Celebrities",
        "Food and Cooking", "Science and Space", "Travel and Tourism", "Health and Wellness"
    ]

    all_categories = []

    for category in categories_list:
        # Getting content form youtube API
        youtube_url = (
            f"https://www.googleapis.com/youtube/v3/search?"
            f"key={YOUTUBE_API_KEY}&part=snippet&type=video&maxResults=2&q={category}"
        )
        yt_response = requests.get(youtube_url).json()
        videos = [{
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"]
        } for item in yt_response.get("items", [])]

        # Getting content from news API
        news_url = (
            f"https://newsapi.org/v2/everything?"
            f"q={category}&pageSize=3&apiKey={NEWS_API_KEY}"
        )
        news_response = requests.get(news_url).json()
        blogs = [{
            "title": article["title"],
            "description": article.get("description", ""),
            "url": article["url"]
        } for article in news_response.get("articles", [])]

        all_categories.append({
            "name": category,
            "videos": videos,
            "blogs": blogs
        })

    return render_template("categories.html", categories=all_categories)


# Route for user uploads. It allows the user to upload their own content.
@app.route("/your_uploads", methods=["GET", "POST"])
def your_uploads():
    emailId = session.get("emailId")
    if not emailId:
        return redirect("/")

    db = ContentDB()

    if request.method == "POST":
        title = request.form.get("title")
        tag = request.form.get("tag")
        link = request.form.get("link")
        if title and tag and link:
            db.add_content(emailId, title, tag, link)

    uploads = db.get_user_content(emailId)
    return render_template("your_uploads.html", uploads=uploads)




@app.route("/dashboard")
def dashboard():
    if "emailId" not in session:
        return redirect("/")

    email = session["emailId"]
    db = UserDB()

    # Fetch user details from the user.db
    with db.connect() as conn:
        cursor = conn.execute(
            "SELECT name, emailId FROM users WHERE emailId = ?", (email,)
        )
        user = cursor.fetchone()
    if not user:
        return " User not found. Please check your login status."

    user_info = {
        "name": user[0],
        "email": user[1]
    }
    return render_template("dashboard.html", user=user_info)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# Route For the search bar in the navbar.
@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return redirect("/home")
    videos = fetch_youtube_videos(query=query, max_results=3)
    articles = fetch_news_articles(query=query, page_size=3)
    return render_template("search.html", query=query, videos=videos, articles=articles)


@app.route("/all_users")
def all_users():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(base_dir, '../DataBase/users.db'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name, emailId FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = [{"name": name, "emailId": email} for name, email in rows]
    return render_template("all_users.html", users=users)

# Route to see the  top picks of all the different users (Based on a fake AI Score.)
@app.route("/user_top_picks/<username>")
def user_top_picks(username):
    mixed_content = []

    # Youtube Content
    try:
        youtube_url = (
            f"https://www.googleapis.com/youtube/v3/search?"
            f"key={YOUTUBE_API_KEY}&part=snippet&type=video&maxResults=10&q=trending"
        )
        yt_response = requests.get(youtube_url).json()
        for item in yt_response.get("items", []):
            mixed_content.append({
                "title": item["snippet"]["title"],
                "tag": "YouTube",
                "link": f"https://www.youtube.com/embed/{item['id']['videoId']}",
                "score": round(random.uniform(0, 1), 2)
            })
    except Exception as e:
        print("YouTube API error:", e)

    # NEWS API Content
    try:
        news_url = (
            f"https://newsapi.org/v2/top-headlines?"
            f"language=en&pageSize=10&apiKey={NEWS_API_KEY}"
        )
        news_response = requests.get(news_url).json()
        for article in news_response.get("articles", []):
            mixed_content.append({
                "title": article["title"],
                "tag": "Blog",
                "link": article["url"],
                "score": round(random.uniform(0, 1), 2)
            })
    except Exception as e:
        print("News API error:", e)

    # Sorting based on fake ai score
    top_5 = sorted(mixed_content, key=lambda x: x["score"], reverse=True)[:5]

    return render_template(
        "top_picks.html",
        picks=top_5,
        current_user=username,
        show_users_btn=False
    )


@app.route("/top_picks")
def top_picks():
    
    try:
        youtube_url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&key={YOUTUBE_API_KEY}&type=video&maxResults=5&order=viewCount"
        )
        yt_response = requests.get(youtube_url)
        yt_response.raise_for_status()
        yt_items = yt_response.json().get("items", [])
        youtube_videos = [
            {
                "title": video["snippet"]["title"],
                "tag": video["snippet"]["channelTitle"],
                "link": f"https://www.youtube.com/embed/{video['id']['videoId']}"
            }
            for video in yt_items
        ]
    except Exception as e:
        print("YouTube API error:", e)
        youtube_videos = []

    try:
        news_url = (
            f"https://newsapi.org/v2/top-headlines"
            f"?language=en&pageSize=5&apiKey={NEWS_API_KEY}"
        )
        news_response = requests.get(news_url)
        news_response.raise_for_status()
        news_items = news_response.json().get("articles", [])
        news_articles = [
            {
                "title": article["title"],
                "tag": article["source"]["name"],
                "link": article["url"]
            }
            for article in news_items
        ]
    except Exception as e:
        print("News API error:", e)
        news_articles = []

    # mixing ontent from both the api's
    mixed_content = youtube_videos + news_articles
    for item in mixed_content:
        item["score"] = round(random.uniform(0, 1), 2)

    # Top 5 based on fake score
    top_5 = sorted(mixed_content, key=lambda x: x["score"], reverse=True)[:5]

    return render_template(
        "top_picks.html",
        picks=top_5,
        current_user=None,
        show_users_btn=True
    )



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

