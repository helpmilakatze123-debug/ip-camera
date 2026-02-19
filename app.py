from flask import Flask, Response, request, render_template_string
import time
import threading

app = Flask(__name__)

latest_frame = None
last_health = 0
viewers = 0
viewers_lock = threading.Lock()

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Live Webcam</title>
</head>
<body>
<h2>Live Webcam Stream</h2>
<img src="/video_feed" width="720">
<p>Client health: {{health}} seconds ago</p>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(PAGE, health=int(time.time() - last_health))

@app.route("/upload_frame", methods=["POST"])
def upload_frame():
    global latest_frame
    latest_frame = request.data
    return "OK"

@app.route("/video_feed")
def video_feed():
    global viewers

    with viewers_lock:
        viewers += 1

    def generate():
        global latest_frame
        try:
            while True:
                if latest_frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
                time.sleep(0.03)  # ~30 FPS
        finally:
            global viewers
            with viewers_lock:
                viewers -= 1

    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/should_stream")
def should_stream():
    return {"stream": viewers > 0}

@app.route("/health", methods=["POST"])
def health():
    global last_health
    last_health = time.time()
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
