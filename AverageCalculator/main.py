from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

# Configuration
WINDOW_SIZE = 10
THIRD_PARTY_API = "http://20.244.56.144/evaluation-service"  # Test server API base URL
TIMEOUT = 0.5  # 500 ms timeout

# State to store numbers
stored_numbers = []

def fetch_num(id):
    try:
        response = requests.get(f"{THIRD_PARTY_API}/{id}", timeout=TIMEOUT)
        if response.status_code == 200:
            return list(set(response.json().get("numbers", [])))  # Ensure uniqueness
    except requests.exceptions.RequestException:
        pass
    return []

@app.route('/numbers/<string:number_id>', methods=['GET'])
def calculate_average(number_id):
    global stored_numbers

    if number_id not in ['primes', 'fibo', 'even', 'rand']:
        return jsonify({"error": "Invalid number ID"}), 400

    # Fetch numbers from third-party API
    numbers = fetch_num(number_id)

    # Prepare previous state
    window_prev_state = stored_numbers.copy()

    # Add new numbers to the window, ensuring uniqueness
    for num in numbers:
        if num not in stored_numbers:
            if len(stored_numbers) >= WINDOW_SIZE:
                stored_numbers.pop(0)  # Remove the oldest number
            stored_numbers.append(num)

    # Calculate average
    avg = round(sum(stored_numbers) / len(stored_numbers), 2) if stored_numbers else 0.0

    # Prepare response
    response = {
        "windowPrevState": window_prev_state,
        "windowCurrState": stored_numbers,
        "numbers": numbers,
        "avg": avg
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)