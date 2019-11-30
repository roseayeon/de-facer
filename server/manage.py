from face_rt import FaceRealTime
from flask import Flask, jsonify, redirect, request, Response, send_from_directory
from flask_cors import CORS, cross_origin
from google.cloud import storage
from urllib.parse import urlparse
from urllib.request import urlretrieve
import ast
import face
import uuid
import os

BUCKET_NAME = "kaist-cs470-project"
STORAGE_URL_FORMAT = "https://storage.googleapis.com/{}/{}"

app = Flask(__name__)
cors = CORS(app)

def init():
    # Create tmp/{targets|videos/replacements/outputs}
    dirs = ["targets", "videos", "replacements", "outputs"]
    for d in dirs:
        path = os.path.join(app.root_path, "tmp", d)
        if not os.path.exists(path):
            os.makedirs(path)
    pass

@app.route('/')
def home():
    return redirect("http://" + urlparse(request.base_url).hostname + ":3000")

@app.route("/robots.txt")
def robot():
    return send_from_directory(app.static_folder, request.path[1:])

def upload_to_storage_from_file(path, file):
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(path)
    blob.upload_from_string(file.read(), content_type=file.content_type)

def upload_to_storage_from_local(path, local_path):
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(path)
    blob.upload_from_filename(local_path)

def load_targets():
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix="targets/", delimiter="/")
    files = []
    for blob in blobs:
        files.append(str.format(STORAGE_URL_FORMAT, BUCKET_NAME, blob.name))
    return files

def random_name():
    return str(uuid.uuid4())

@app.route("/targets", methods=["GET", "POST"])
@cross_origin()
def get_target_images():
    if request.method == 'GET':
        return jsonify({"images": load_targets()})
    else:
        # Upload
        image = request.files["image"]
        path = "targets/" + image.filename
        upload_to_storage_from_file(path, image)
        return Response()

# Receive Video / Target Images' URLs / Replacement Image(Optional) to de-face the video
@app.route("/process", methods=["POST"])
@cross_origin()
def process():
    try:
        uid = random_name()

        input_path = None
        targets_path = []
        replace_path = None # to blur, should be None
        output_path = os.path.join(app.root_path, "tmp", "outputs", uid + ".avi")

        video = request.files["video"]
        input_path = os.path.join(app.root_path, "tmp", "videos", uid)
        video.save(input_path)
        gcp_output_path = "outputs/" + video.filename.split(".")[0] + "-defaced.avi"

        targets_path_raw = ast.literal_eval(request.form["targets"])
        for idx, path_raw in enumerate(targets_path_raw):
            path = os.path.join(app.root_path, "tmp", "targets", "{}_{}".format(uid, idx))
            urlretrieve(path_raw, path)
            targets_path.append(path)

        if "replacement" in request.files:
            replacement = request.files["replacement"]
            replace_path = os.path.join(app.root_path, "tmp", "replacements", uid)
            replacement.save(replace_path)

        face.process_video(input_path, targets_path, replace_path, output_path)
        upload_to_storage_from_local(gcp_output_path, output_path)

        return jsonify({"url": str.format(STORAGE_URL_FORMAT, BUCKET_NAME, gcp_output_path)})
    finally:
        if input_path is not None:
            os.remove(input_path)
        for path in targets_path:
            os.remove(path)
        if replace_path is not None:
            os.remove(replace_path)
        if os.path.isfile(output_path):
            os.remove(output_path)

REALTIME_URL = ""
REALTIME_TARGETS_PATH = []
REALTIME_REPLACEMENT_PATH = ""

def gen():
    face_realtime = FaceRealTime(REALTIME_URL, REALTIME_TARGETS_PATH, REALTIME_REPLACEMENT_PATH)
    while True:
        jpg_bytes = face_realtime.get_jpg_bytes()
        if jpg_bytes == None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n\r\n')

# Receive Realtime video URL / Target Images' URLs / Replacement Image URL(Optional) to de-face in real-time.
@app.route("/live", methods=["POST"])
@cross_origin()
def live():
    global REALTIME_URL, REALTIME_TARGETS_PATH, REALTIME_REPLACEMENT_PATH
    uid = random_name()
    REALTIME_TARGETS_PATH = []
    REALTIME_REPLACEMENT_PATH = None

    REALTIME_URL = request.form["url"]
    targets_path_raw = ast.literal_eval(request.form["targets"])
    for idx, path_raw in enumerate(targets_path_raw):
        path = os.path.join(app.root_path, "tmp", "targets", "{}_{}".format(uid, idx))
        urlretrieve(path_raw, path)
        REALTIME_TARGETS_PATH.append(path)

    if "replacement" in request.files:
        replacement = request.files["replacement"]
        REALTIME_REPLACEMENT_PATH = os.path.join(app.root_path, "tmp", "replacements", uid)
        replacement.save(REALTIME_REPLACEMENT_PATH)

    return Response()

@app.route("/real_time")
def real_time():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    init()
    app.run(host='0.0.0.0', port=80, debug=True)
