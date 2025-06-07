import os
from flask import Flask, jsonify, request, send_from_directory, Response
from flasgger import Swagger
from flask_cors import CORS
import requests
import urllib
from lib_version.versionuntil.version_until import VersionUtil
from prometheus_client import Counter, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST



app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

#Counter
REQUEST_COUNT = Counter("app_requests_total", "Total number of app requests")


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
    # url = urllib.parse.urljoin(MODEL_SERVICE_URL, "api/version")
    # response = requests.get(url)
    # # TODO: update parameter
    # model_service_version = response.json().get("version")
    # TODO: import lib-version
    return {
        "appVersion": VersionUtil.get_version(),
        # TODO: fix this
        "modelServiceVersion": "0.0.1",
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
    #incrementing counter everytime invoked
    REQUEST_COUNT.inc()

    review = request.get_json().get("review")
    url = urllib.parse.urljoin(MODEL_SERVICE_URL, "predict")
    data = {"review": review}
    headers = {"Content-Type": "application/json"}
    print(f"Sending request to {url} with data: {data}")
    response = requests.post(url, json=data, headers=headers)
    sentiment = response.json().get("result")

    return jsonify({"sentiment": sentiment})

@app.route("/metrics")
def metrics():
    """
    ---
    description: Get the metrics of the service
    responses:
      200:
        description: The metrics of the service
    """
    #prometheus client lib - gathering registered metrics
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


app.run(
    host="0.0.0.0",
    port=8080,
    debug=True,  # TODO: run in release mode
)
