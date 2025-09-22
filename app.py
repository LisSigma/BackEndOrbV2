from flask import Flask, request, jsonify

app = Flask(__name__)
messages = []  # in-memory message storage

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json()
    user = data.get("user", "anon")
    text = data.get("text", "")
    messages.append({"user": user, "text": text})
    return jsonify({"status": "ok"})

@app.route("/messages", methods=["GET"])
def get_messages():
    return jsonify(messages)

if __name__ == "__main__":
    # Render will set the PORT env var automatically
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
