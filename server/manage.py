from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS, cross_origin
from google.cloud import storage
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
def hello_world():
    return 'Team 13 AI Project'

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

@app.route("/process", methods=["POST"])
@cross_origin()
def process():
    try:
        uid = random_name()

        input_path = None
        targets_path = []
        replace_path = None # to blur, should be None
        output_path = os.path.join(app.root_path, "tmp", "outputs", uid)
        gcp_output_path = "targets/" + uid

        video = request.files["video"]
        input_path = os.path.join(app.root_path, "tmp", "videos", uid)
        video.save(input_path)

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

        return jsonify({"url": gcp_output_path})
    finally:
        if input_path is not None:
            os.remove(input_path)
        for path in targets_path:
            os.remove(path)
        if replace_path is not None:
            os.remove(replace_path)
        if os.path.isfile(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    init()
    app.run(host='0.0.0.0', port=80)
