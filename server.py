import os
from flask import Flask, jsonify, request, send_from_directory
from flasgger import Swagger
from flask_cors import CORS
import requests
import urllib
from lib_version import VersionUtil


app = Flask(__name__)
CORS(app)
swagger = Swagger(app)


MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL")
if MODEL_SERVICE_URL is None:
    raise ValueError("MODEL_SERVICE_URL is not set")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join("frontend/dist", path)):
        return send_from_directory("frontend/dist", path)
    else:
        return send_from_directory("frontend/dist", "index.html")


@app.route("/api/version", methods=["GET"])
def get_version():
    """
    ---
    description: Get the version of the service
    responses:
      200:
        description: The version of the service
        schema:
          type: object
          properties:
            app_version:
              type: string
            model_service_version:
              type: string
    """

    # TODO: update url
    url = urllib.parse.urljoin(MODEL_SERVICE_URL, "/api/version")
    response = requests.get(url)
    # TODO: update parameter
    model_service_version = response.json().get("version")
    # TODO: import lib-version
    return {
        "app_version": VersionUtil.get_version(),
        # TODO: fix this
        "model_service_version": "v0.0.1",
    }


@app.route("/api/query", methods=["POST"])
def query_model():
    """
    ---
    description: Query the model-service
    parameters:
      - name: review
        in: body
        required: true
        schema:
          type: object
          properties:
            review:
              type: string

    responses:
      200:
        description: The response from the model-service
        schema:
          type: object
          properties:
            sentiment:
              type: string
    """

    review = request.get_json().get("review")
    url = urllib.parse.urljoin(MODEL_SERVICE_URL, "/predict")
    data = {"review": review}
    response = requests.post(url, json=data)
    sentiment = response.json().get("sentiment")

    return jsonify({"sentiment": sentiment})


app.run(
    host="0.0.0.0",
    port=8080,
    debug=True,  # TODO: run in release mode
)
