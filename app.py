from flask import Flask, Response, request, render_template_string
import time

app = Flask(__name__()

)
latest_frame = None
last_health = 0
stream_active = False

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Live Webcam</title>
</head>
<body>
<h2>Live Stream</h2>
<img src="/video_feed" width="720">
<p>Client health: {{health}} seconds ago</p>
</body>
</html>
"""

@app.route("/")
def index():
    global stream_active
    stream_active = True
    return render_template_string(PAGE, health=int(time.time() - last_health))

@app.route("/video_feed")
def video_feed():
    global stream_active
    stream_active = True

    def generate():
        global latest_frame
        while True:
            if latest_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
            else:
                time.sleep(0.01)

    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/upload_stream", methods=["POST"])
def upload_stream():
    global latest_frame
    stream = request.stream
    while True:
        chunk = stream.read(4096)
        if not chunk:
            break
        latest_frame = chunk
    return "OK"

@app.route("/should_stream")
def should_stream():
    return {"stream": stream_active}

@app.route("/health", methods=["POST"])
def health():
    global last_health
    last_health = time.time()
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
