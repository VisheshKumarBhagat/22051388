from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
PORT = 9876
WINDOW_SIZE = 10

AUTH_URL = "http://20.244.56.144/evaluation-service/auth"
API_URLS = {
    "p": "http://20.244.56.144/evaluation-service/primes",
    "f": "http://20.244.56.144/evaluation-service/fibo",
    "e": "http://20.244.56.144/evaluation-service/even",
    "r": "http://20.244.56.144/evaluation-service/rand"
}

ACCESS_TOKEN = None
number_window = []

def fetch_new_token():
    """Fetch a new access token from the authentication service."""
    global ACCESS_TOKEN
    try:
        print("Fetching new access token...")
        response = requests.post(AUTH_URL, json={
            "email": "22051388@kiit.ac.in",
            "name": "vishesh kumar bhagat",
            "rollNo": "22051388",
            "accessCode": "nwpwrZ",
            "clientID": "d56eb03e-d1eb-4556-9f90-6c6e776b8661",
            "clientSecret": "MvhXgVnuPjDzCWwT"
        }, headers={"Content-Type": "application/json"})

        response.raise_for_status()
        ACCESS_TOKEN = response.json().get("access_token")
        print("New Access Token Acquired:", ACCESS_TOKEN)
    except requests.exceptions.RequestException as e:
        print("Error fetching token:", e)
        ACCESS_TOKEN = None

def fetch_numbers(number_id):
    """Fetch numbers from the specified API using the access token."""
    global ACCESS_TOKEN
    if not ACCESS_TOKEN:
        fetch_new_token()
        if not ACCESS_TOKEN:
            return []

    try:
        source_url = API_URLS[number_id]
        print(f'{source_url}, {ACCESS_TOKEN}')
        response = requests.get(source_url, headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }, timeout=0.5)

        response.raise_for_status()
        return response.json().get("numbers", [])
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:  # Unauthorized
            print("401 Unauthorized! Fetching new token and retrying...")
            fetch_new_token()
            return fetch_numbers(number_id)
        print(f"Error fetching numbers from {number_id}:", e)
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching numbers from {number_id}:", e)
        return []

def update_window(new_numbers):
    """Update the sliding window with new numbers and calculate the average."""
    global number_window
    prev_state = number_window[:]

    for num in new_numbers:
        if num not in number_window:
            if len(number_window) >= WINDOW_SIZE:
                number_window.pop(0)
            number_window.append(num)

    avg = round(sum(number_window) / len(number_window), 2) if number_window else 0
    return {"prevState": prev_state, "currState": number_window[:], "avg": avg}

@app.route("/numbers/<number_id>", methods=["GET"])
def get_numbers(number_id):
    """API endpoint to fetch numbers and update the sliding window."""
    if number_id not in API_URLS:
        return jsonify({"error": "Invalid number ID"}), 400

    # Step 1: Ensure we have a valid access token
    if not ACCESS_TOKEN:
        fetch_new_token()
        if not ACCESS_TOKEN:
            return jsonify({"error": "Unable to fetch access token"}), 500

    # Step 2: Fetch numbers from the API
    numbers = fetch_numbers(number_id)
    if not numbers:
        return jsonify({"error": "Unable to fetch numbers"}), 500

    # Step 3: Update the sliding window and calculate the average
    result = update_window(numbers)

    return jsonify({
        "windowPrevState": result["prevState"],
        "windowCurrState": result["currState"],
        "numbers": numbers,
        "avg": result["avg"]
    })

if __name__ == "__main__":
    print(f"Server running on http://localhost:{PORT}")
    fetch_new_token()
    app.run(port=PORT)
