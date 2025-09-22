from flask import Flask, request, jsonify
import json
import os
import hashlib
import uuid
import socket

app = Flask(__name__)

# Preloaded keys (any keys you want to allow)
PRELOADED_KEYS = [
    "8#zP$vR2!yA9-nF6gB4^tH3*eD7qV5@sL9&zW1*xJ4!cO8#pU2$kY6bN7^mZ1%",
    "sA3^mP8hT2!jF6-gC9$vB5*nK1@dE5*rT8#uI2%oP6-aL4^zQ1@xW7yB9-nF6",
    "pU2$kY6bN7^mZ1%eR4@tG8*uI3-kL6#oP9qV5@sL9&zW1*xJ4!cO8#8#zP$vR2",
    "gC9$vB5*nK1@sA3^mP8hT2!jF6-aL4^zQ1@xW7dE5*rT8#uI2%oP6-nF6gB4^",
    "uI3-kL6#oP9qV5@sL9&zW1*xJ4!cO8#pU2$kY6bN7^mZ1%eR4@tG8*yA9-nF6g"
]

DB_FILE = "keys.json"

# Initialize DB with preloaded keys
if not os.path.exists(DB_FILE):
    keys = {key: {} for key in PRELOADED_KEYS}
    with open(DB_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def load_keys():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_hwid():
    mac = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
    hwid = hashlib.sha256((socket.gethostname() + mac).encode()).hexdigest()
    return hwid

@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")
    ip = request.remote_addr

    if not key or not hwid:
        return jsonify({"status": "error", "message": "Key and HWID required"}), 400

    keys = load_keys()

    if key not in keys:
        return jsonify({"status": "error", "message": "Invalid key"}), 403

    key_info = keys[key]

    # Check if already used
    if "ip" in key_info and key_info["ip"] != ip:
        return jsonify({"status": "error", "message": "Key already used from another IP"}), 403
    if "hwid" in key_info and key_info["hwid"] != hwid:
        return jsonify({"status": "error", "message": "Key already used on another machine"}), 403

    # Bind IP and HWID
    key_info["ip"] = ip
    key_info["hwid"] = hwid
    keys[key] = key_info
    save_keys(keys)

    return jsonify({"status": "success", "message": "Key validated"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
