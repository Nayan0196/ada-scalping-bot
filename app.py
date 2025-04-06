from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DELTA_API_KEY = os.getenv("DELTA_API_KEY")
DELTA_SECRET_KEY = os.getenv("DELTA_SECRET_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Received data:", data)

    side = data.get("side")  # 'buy' or 'sell'
    symbol = "ADAUSDT"
    quantity = 10
    take_profit_pct = 0.008
    stop_loss_pct = 0.005

    order_price = float(data.get("price", 0.64))
    take_profit = order_price * (1 + take_profit_pct if side == "buy" else 1 - take_profit_pct)
    stop_loss = order_price * (1 - stop_loss_pct if side == "buy" else 1 + stop_loss_pct)

    place_order(symbol, side, quantity, order_price, take_profit, stop_loss)
    return jsonify({"status": "Order sent"}), 200

def generate_signature(api_secret, timestamp, method, path, body=""):
    payload = f"{timestamp}{method}{path}{body}"
    return hmac.new(
        api_secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()

def place_order(symbol, side, quantity, price, take_profit, stop_loss):
    url = "https://api.delta.exchange/orders"
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    path = "/orders"

    body = {
        "product_id": 142,
        "limit_price": None,
        "order_type": "market",
        "side": side,
        "size": quantity,
        "stop_loss": {
            "type": "price",
            "value": round(stop_loss, 5)
        },
        "take_profit": {
            "type": "price",
            "value": round(take_profit, 5)
        }
    }

    import json
    body_json = json.dumps(body)
    signature = generate_signature(DELTA_SECRET_KEY, timestamp, method, path, body_json)

    headers = {
        "api-key": DELTA_API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=body_json)
    print("Delta API response:", response.status_code, response.text)

# 🚀 Add this to run the app!
if __name__ == '__main__':
    app.run(debug=True)
