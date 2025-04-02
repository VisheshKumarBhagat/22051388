from flask import Flask, request, jsonify
import requests
from collections import defaultdict
from operator import itemgetter

app = Flask(__name__)

BASE_URL = "http://20.244.56.144/evaluation-service"

# Cache to minimize API calls
user_post_count_cache = {}
post_comment_count_cache = {}
latest_posts_cache = []

@app.route('/users', methods=['GET'])
def top_users():
    global user_post_count_cache

    # Fetch users
    users_response = requests.get(f"{BASE_URL}/users")
    users = users_response.json().get("users", {})

    # Fetch posts for each user and count them
    for user_id in users.keys():
        if user_id not in user_post_count_cache:
            posts_response = requests.get(f"{BASE_URL}/users/{user_id}/posts")
            posts = posts_response.json().get("posts", [])
            user_post_count_cache[user_id] = len(posts)

    # Sort users by post count and get the top 5
    top_users = sorted(user_post_count_cache.items(), key=itemgetter(1), reverse=True)[:5]
    result = [{"user_id": user_id, "name": users[user_id], "post_count": count} for user_id, count in top_users]

    return jsonify(result)

@app.route('/posts', methods=['GET'])
def top_or_latest_posts():
    global post_comment_count_cache, latest_posts_cache

    post_type = request.args.get('type', 'latest')

    if post_type == 'popular':
        # Fetch all posts and their comment counts
        if not post_comment_count_cache:
            users_response = requests.get(f"{BASE_URL}/users")
            users = users_response.json().get("users", {})
            for user_id in users.keys():
                posts_response = requests.get(f"{BASE_URL}/users/{user_id}/posts")
                posts = posts_response.json().get("posts", [])
                for post in posts:
                    post_id = post["id"]
                    comments_response = requests.get(f"{BASE_URL}/posts/{post_id}/comments")
                    comments = comments_response.json().get("comments", [])
                    post_comment_count_cache[post_id] = len(comments)

        # Find the post(s) with the maximum number of comments
        max_comments = max(post_comment_count_cache.values(), default=0)
        popular_posts = [post_id for post_id, count in post_comment_count_cache.items() if count == max_comments]

        return jsonify({"popular_posts": popular_posts})

    elif post_type == 'latest':
        # Fetch latest posts
        if not latest_posts_cache:
            users_response = requests.get(f"{BASE_URL}/users")
            users = users_response.json().get("users", {})
            all_posts = []
            for user_id in users.keys():
                posts_response = requests.get(f"{BASE_URL}/users/{user_id}/posts")
                posts = posts_response.json().get("posts", [])
                all_posts.extend(posts)
            latest_posts_cache = sorted(all_posts, key=lambda x: x["id"], reverse=True)[:5]

        return jsonify({"latest_posts": latest_posts_cache})

    else:
        return jsonify({"error": "Invalid type parameter. Use 'popular' or 'latest'."}), 400

if __name__ == '__main__':
    app.run(debug=True)