from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Allowed keys
VALID_KEYS = [
    "8#zP$vR2!yA9-nF6gB4^tH3*eD7qV5@sL9&zW1*xJ4!cO8#pU2$kY6bN7^mZ1%",
    "sA3^mP8hT2!jF6-gC9$vB5*nK1@dE5*rT8#uI2%oP6-aL4^zQ1@xW7yB9-nF6",
    "pU2$kY6bN7^mZ1%eR4@tG8*uI3-kL6#oP9qV5@sL9&zW1*xJ4!cO8#8#zP$vR2",
    "gC9$vB5*nK1@sA3^mP8hT2!jF6-aL4^zQ1@xW7dE5*rT8#uI2%oP6-nF6gB4^",
    "uI3-kL6#oP9qV5@sL9&zW1*xJ4!cO8#pU2$kY6bN7^mZ1%eR4@tG8*yA9-nF6g"
]

DB_FILE = "keys.json"

# Initialize DB
if not os.path.exists(DB_FILE):
    data = {key: {} for key in VALID_KEYS}
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_keys():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    key = data.get("key")
    ip = request.remote_addr

    if not key:
        return jsonify({"status": "error", "message": "Key required"}), 400

    keys = load_keys()

    if key not in keys:
        return jsonify({"status": "error", "message": "Invalid key"}), 403

    key_info = keys[key]

    # Check if already bound to another IP
    if "ip" in key_info and key_info["ip"] != ip:
        return jsonify({"status": "error", "message": "Key already used from another IP"}), 403

    # Bind IP
    key_info["ip"] = ip
    keys[key] = key_info
    save_keys(keys)

    return jsonify({"status": "success", "message": "Key valid and bound to your IP"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
