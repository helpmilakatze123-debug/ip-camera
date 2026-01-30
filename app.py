from flask import Flask, Response
import os

app = Flask(__name__)

HTML_PATH = "index.html"

@app.route("/")
@app.route("/index.html")
def serve_index():
    if not os.path.exists(HTML_PATH):
        return "index.html nicht gefunden", 404

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Kein Browser-Cache → immer neu laden
    return Response(
        html_content,
        mimetype="text/html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

if __name__ == "__main__":
    # 0.0.0.0 = von außen erreichbar (Cloud!)
    app.run(host="0.0.0.0", port=80)
