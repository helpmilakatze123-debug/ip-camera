from flask import Flask, Response, request, render_template_string
import time

app = Flask(__name__)

latest_frame = None
last_health = 0
stream_requested = False

PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Webcam Live View</title>
</head>
<body>
    <h2>Live Webcam</h2>
    <img src="/video_feed" width="640">
    <p>Last client health ping: {{health}} seconds ago</p>
</body>
</html>
"""

@app.route("/")
def index():
    global stream_requested
    stream_requested = True
    return render_template_string(PAGE, health=int(time.time() - last_health))

@app.route("/upload_frame", methods=["POST"])
def upload_frame():
    global latest_frame
    latest_frame = request.data
    return "OK"

@app.route("/video_feed")
def video_feed():
    def generate():
        global latest_frame
        while True:
            if latest_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
            time.sleep(0.03)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/should_stream")
def should_stream():
    return {"stream": stream_requested}

@app.route("/health", methods=["POST"])
def health():
    global last_health
    last_health = time.time()
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
