from flask import Flask, request, jsonify
import requests
from collections import defaultdict
from operator import itemgetter

app = Flask(__name__)

# Base URL for the test server
BASE_URL = "http://20.244.56.144/evaluation-service"
AUTH_URL = "http://20.244.56.144/evaluation-service/auth"

# Authorization token
AUTH_TOKEN = None


def get_auth_token():
    global AUTH_TOKEN
    if AUTH_TOKEN is None:
        response = requests.post(AUTH_URL, json={
            "email": "22051388@kiit.ac.in",
            "name": "vishesh kumar bhagat",
            "rollNo": "22051388",
            "accessCode": "nwpwrZ",
            "clientID": "d56eb03e-d1eb-4556-9f90-6c6e776b8661",
            "clientSecret": "MvhXgVnuPjDzCWwT"
        }, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        AUTH_TOKEN = response.json().get("access_token")
    return AUTH_TOKEN


def fetch_users():
    headers = {"Authorization": f"Bearer {get_auth_token()}"}
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    response.raise_for_status()
    return response.json()["users"]


def fetch_user_posts(user_id):
    headers = {"Authorization": f"Bearer {get_auth_token()}"}
    response = requests.get(f"{BASE_URL}/users/{user_id}/posts", headers=headers)
    response.raise_for_status()
    return response.json()["posts"]


def fetch_post_comments(post_id):
    headers = {"Authorization": f"Bearer {get_auth_token()}"}
    response = requests.get(f"{BASE_URL}/posts/{post_id}/comments", headers=headers)
    response.raise_for_status()
    return response.json()["comments"]


@app.route('/users', methods=['GET'])
def top_users():
    users = fetch_users()
    user_post_counts = defaultdict(int)

    for user_id in users.keys():
        posts = fetch_user_posts(user_id)
        user_post_counts[user_id] = len(posts)

    # Get top 5 users with the highest number of posts
    top_users = sorted(user_post_counts.items(), key=itemgetter(1), reverse=True)[:5]
    result = [{"user_id": user_id, "name": users[user_id], "post_count": count} for user_id, count in top_users]

    return jsonify(result)

@app.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    users = fetch_users()

    if str(user_id) not in users:
        return jsonify({"error": "User not found"}), 404

    # Fetch posts for the given user ID
    posts = fetch_user_posts(user_id)

    return jsonify(posts)


@app.route('/posts', methods=['GET'])
def top_or_latest_posts():
    post_type = request.args.get('type', 'latest')

    users = fetch_users()
    all_posts = []

    # Fetch all posts from all users
    for user_id in users.keys():
        all_posts.extend(fetch_user_posts(user_id))

    if post_type == 'popular':
        # Fetch comments for each post and count them
        post_comment_counts = []
        for post in all_posts:
            comments = fetch_post_comments(post["id"])
            post_comment_counts.append({"post": post, "comment_count": len(comments)})

        if not post_comment_counts:
            return jsonify([])  # Return an empty list if there are no posts

        # Get posts with the maximum number of comments
        max_comments = max(post_comment_counts, key=lambda x: x["comment_count"])["comment_count"]
        popular_posts = [entry["post"] for entry in post_comment_counts if entry["comment_count"] == max_comments]

        return jsonify(popular_posts)

    elif post_type == 'latest':
        # Sort posts by their IDs (assuming higher IDs are newer)
        latest_posts = sorted(all_posts, key=lambda x: x["id"], reverse=True)[:5]
        return jsonify(latest_posts)

    else:
        return jsonify({"error": "Invalid type parameter. Accepted values are 'latest' or 'popular'."}), 400


@app.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    user_id = request.args.get('user_id')

    # Fetch comments for the given post ID
    comments = fetch_post_comments(post_id)

    if user_id:
        # Filter comments by the given user ID
        comments = [comment for comment in comments if comment["user_id"] == int(user_id)]

    return jsonify(comments)

if __name__ == '__main__':
    app.run(debug=True)
