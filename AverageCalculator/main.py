from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
PORT = 9876
WINDOW_LIMIT = 10

AUTH_ENDPOINT = "http://20.244.56.144/evaluation-service/auth"
SERVICE_URLS = {
    "p": "http://20.244.56.144/evaluation-service/primes",
    "f": "http://20.244.56.144/evaluation-service/fibo",
    "e": "http://20.244.56.144/evaluation-service/even",
    "r": "http://20.244.56.144/evaluation-service/rand"
}

TOKEN = None
sliding_window = []

def retrieve_access_token():
    """Retrieve a fresh access token from the authentication endpoint."""
    global TOKEN
    try:
        print("Requesting a new access token...")
        response = requests.post(AUTH_ENDPOINT, json={
            "email": "22051388@kiit.ac.in",
            "name": "vishesh kumar bhagat",
            "rollNo": "22051388",
            "accessCode": "nwpwrZ",
            "clientID": "d56eb03e-d1eb-4556-9f90-6c6e776b8661",
            "clientSecret": "MvhXgVnuPjDzCWwT"
        }, headers={"Content-Type": "application/json"})

        response.raise_for_status()
        TOKEN = response.json().get("access_token")
        print("Access token retrieved:", TOKEN)
    except requests.exceptions.RequestException as error:
        print("Failed to retrieve token:", error)
        TOKEN = None

def get_numbers_from_service(service_id):
    """Fetch numbers from the specified service using the current token."""
    global TOKEN
    if not TOKEN:
        retrieve_access_token()
        if not TOKEN:
            return []

    try:
        service_url = SERVICE_URLS[service_id]
        print(f"Requesting numbers from {service_url} with token {TOKEN}")
        response = requests.get(service_url, headers={
            "Authorization": f"Bearer {TOKEN}"
        }, timeout=0.5)

        response.raise_for_status()
        return response.json().get("numbers", [])
    except requests.exceptions.HTTPError as error:
        if response.status_code == 401:  # Unauthorized
            print("Token expired. Fetching a new token and retrying...")
            retrieve_access_token()
            return get_numbers_from_service(service_id)
        print(f"HTTP error while fetching numbers from {service_id}:", error)
        return []
    except requests.exceptions.RequestException as error:
        print(f"Request error while fetching numbers from {service_id}:", error)
        return []

def update_sliding_window(new_numbers):
    """Update the sliding window with new numbers and compute the average."""
    global sliding_window
    previous_state = sliding_window[:]

    for number in new_numbers:
        if number not in sliding_window:
            if len(sliding_window) >= WINDOW_LIMIT:
                sliding_window.pop(0)
            sliding_window.append(number)

    average = round(sum(sliding_window) / len(sliding_window), 2) if sliding_window else 0
    return {"previousState": previous_state, "currentState": sliding_window[:], "average": average}

@app.route("/numbers/<service_id>", methods=["GET"])
def handle_numbers_request(service_id):
    """API endpoint to fetch numbers and update the sliding window."""
    if service_id not in SERVICE_URLS:
        return jsonify({"error": "Invalid service ID"}), 400

    # Step 1: Ensure a valid token is available
    if not TOKEN:
        retrieve_access_token()
        if not TOKEN:
            return jsonify({"error": "Failed to retrieve access token"}), 500

    # Step 2: Fetch numbers from the service
    numbers = get_numbers_from_service(service_id)
    if not numbers:
        return jsonify({"error": "Failed to fetch numbers"}), 500

    # Step 3: Update the sliding window and calculate the average
    result = update_sliding_window(numbers)

    return jsonify({
        "windowPreviousState": result["previousState"],
        "windowCurrentState": result["currentState"],
        "numbers": numbers,
        "average": result["average"]
    })

if __name__ == "__main__":
    print(f"Server is running at http://localhost:{PORT}")
    retrieve_access_token()
    app.run(port=PORT)
