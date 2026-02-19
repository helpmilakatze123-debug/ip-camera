from flask import Flask, Response, request, render_template_string, jsonify
import time
import threading

app = Flask(__name__)

latest_frame = None
last_health = 0
viewers = 0
selected_camera = 0
lock = threading.Lock()

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Camera Stream</title>
</head>
<body>

<h2>Live Stream</h2>

<label>Kamera auswählen:</label>
<select id="camSelect" onchange="changeCam()">
  <option value="0">Camera 0</option>
  <option value="1">Camera 1</option>
  <option value="2">Camera 2</option>
  <option value="3">Camera 3</option>
</select>

<br><br>

<img src="/video_feed" width="800">

<script>
function changeCam(){
    const cam = document.getElementById("camSelect").value;
    fetch("/set_camera/" + cam);
}
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return PAGE

@app.route("/set_camera/<int:cam>")
def set_camera(cam):
    global selected_camera
    selected_camera = cam
    return "OK"

@app.route("/video_feed")
def video_feed():
    global viewers

    with lock:
        viewers += 1

    def generate():
        global latest_frame
        try:
            while True:
                if latest_frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
                else:
                    time.sleep(0.01)
        finally:
            global viewers
            with lock:
                viewers -= 1

    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/upload_frame", methods=["POST"])
def upload_frame():
    global latest_frame
    latest_frame = request.data
    return "OK"

@app.route("/control")
def control():
    return jsonify({
        "stream": viewers > 0,
        "camera": selected_camera
    })

@app.route("/health", methods=["POST"])
def health():
    global last_health
    last_health = time.time()
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
