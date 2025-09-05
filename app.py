from flask import Flask, request, jsonify

app = Flask(__name__)

# Allowed PlayFab IDs
ALLOWED_IDS = ["1491EDD0C6AA1B9D"]  # <-- replace/add IDs here

@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json()
    playfab_id = data.get("playfab_id")
    if not playfab_id:
        return jsonify({"status": "error", "message": "No PlayFabId provided"}), 400

    if playfab_id in ALLOWED_IDS:
        return jsonify({"status": "success", "message": "Authorized"})
    else:
        return jsonify({"status": "fail", "message": "Unauthorized"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
