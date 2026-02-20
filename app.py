from flask import Flask, request, send_file, jsonify
import json
import os

app = Flask(__name__)

FILE = "tunnel.json"


def save_url(url):
    with open(FILE, "w") as f:
        json.dump({"url": url}, f)


def load_url():
    if os.path.exists(FILE):
        with open(FILE) as f:
            return json.load(f)["url"]
    return None


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/update_tunnel", methods=["POST"])
def update_tunnel():
    data = request.json
    url = data["url"]

    save_url(url)

    print("Neue Tunnel URL gespeichert:", url)

    return "saved"


@app.route("/get_tunnel")
def get_tunnel():
    url = load_url()
    return jsonify({"url": url})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
