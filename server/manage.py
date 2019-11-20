from flask import Flask, jsonify
from google.cloud import storage

BUCKET_NAME = "kaist-cs470-project"
STORAGE_URL_FORMAT = "https://storage.googleapis.com/{}/{}"

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route("/targets", methods=["GET"])
def get_target_images():
    # TODO: Filter the images with mimetype
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)

    images = []
    blobs = bucket.list_blobs(prefix="targets/", delimiter="/")
    for blob in blobs:
        images.append(str.format(STORAGE_URL_FORMAT, BUCKET_NAME, blob.name))
    
    return jsonify({"images": images})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

