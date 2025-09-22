from flask import Flask, request, jsonify
import json
import os
import hashlib
import uuid
import socket

app = Flask(__name__)

# Simple JSON "database"
DB_FILE = "keys.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

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

    # Check IP binding
    if "ip" in key_info and key_info["ip"] != ip:
        return jsonify({"status": "error", "message": "Key already used from another IP"}), 403
    # Check HWID binding
    if "hwid" in key_info and key_info["hwid"] != hwid:
        return jsonify({"status": "error", "message": "Key already used on another machine"}), 403

    # Bind IP and HWID
    key_info["ip"] = ip
    key_info["hwid"] = hwid
    keys[key] = key_info
    save_keys(keys)

    return jsonify({"status": "success", "message": "Key validated"})

@app.route("/create_key", methods=["POST"])
def create_key():
    data = request.json
    key = data.get("key")
    if not key:
        return jsonify({"status": "error", "message": "Key required"}), 400

    keys = load_keys()
    if key in keys:
        return jsonify({"status": "error", "message": "Key already exists"}), 400

    keys[key] = {}  # No binding yet
    save_keys(keys)
    return jsonify({"status": "success", "message": f"Key {key} created"})

@app.route("/list_keys", methods=["GET"])
def list_keys():
    keys = load_keys()
    return jsonify(keys)

if __name__ == "__main__":
    # Run on all interfaces so Render can access it
    app.run(host="0.0.0.0", port=5000)
