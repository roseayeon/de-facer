from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS, cross_origin
from google.cloud import storage
import face

BUCKET_NAME = "kaist-cs470-project"
STORAGE_URL_FORMAT = "https://storage.googleapis.com/{}/{}"

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route("/targets", methods=["GET", "POST"])
@cross_origin()
def get_target_images():
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    if request.method == 'GET':
        # TODO: Filter the images with mimetype

        images = []
        blobs = bucket.list_blobs(prefix="targets/", delimiter="/")
        for blob in blobs:
            images.append(str.format(STORAGE_URL_FORMAT, BUCKET_NAME, blob.name))

        return jsonify({"images": images})
    else:
        # Upload
        image = request.files["image"]
        path = "targets/" + image.filename
        blob = bucket.blob(path)
        blob.upload_from_string(image.read(), content_type=image.content_type)
        return Response()



@app.route("/process", methods=["POST"])
@cross_origin()
def process():
    video = request.files["video"]
    target = request.form["target"]

    input_path = ""
    targets_path = [""]
    replace_path = "" # to blur, should be empty
    output_path = ""
    #face.process_video(input_path, targets_path, replace_path, output_path)
    return Response(stream_with_context(video.stream), mimetype=video.mimetype)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
