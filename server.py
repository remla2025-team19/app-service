import os
from flask import Flask, jsonify, request, send_from_directory
from flasgger import Swagger
from flask_cors import CORS
import requests
import urllib
from lib_version import VersionUtil
from google.cloud import storage
import json


app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

feedback_stats = {
    "total": 0,
    "positive": 0,
    "negative": 0
}


MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL")
if MODEL_SERVICE_URL is None:
    raise ValueError("MODEL_SERVICE_URL is not set")


def upload_feedback(feedback_text, filename="feedback.json"):
    #client = storage.Client.from_service_account_json("remla_secret.json")
    secret_path = os.getenv("GCP_SECRET_PATH")
    if not secret_path:
        raise ValueError("GCP_SECRET_PATH is not set")
    client = storage.Client.from_service_account_json(secret_path)
    bucket = client.bucket("remla2025-team19-bucket")
    blob = bucket.blob(f"feedback/{filename}")
    blob.upload_from_string(feedback_text)


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

@app.route("/api/feedback", methods=["POST"])
def receive_feedback():
    data = request.get_json()
    query = data.get("query")
    feedback_value = data.get("feedback")  # expects 1 or 0

    feedback_stats["total"] += 1
    if feedback_value == 1:
        feedback_stats["positive"] += 1
    elif feedback_value == 0:
        feedback_stats["negative"] += 1

    print(f"Feedback received: {feedback_value} for query: \"{query}\"")
    print("Updated feedback stats:", feedback_stats)

    feedback_json = json.dumps(feedback_stats, indent=4)
    try:
        upload_feedback(feedback_json)
    except Exception as e:
        print(f"Error uploading feedback: {e}")
        return jsonify({"status": "Error uploading feedback"}), 500

    return jsonify({
        "status": "Feedback received",
        "current_stats": feedback_stats
    }), 200



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
    url = urllib.parse.urljoin(MODEL_SERVICE_URL, "predict")
    data = {"review": review}
    headers = {"Content-Type": "application/json"}
    print(f"Sending request to {url} with data: {data}")
    response = requests.post(url, json=data, headers=headers)
    sentiment = response.json().get("result")

    return jsonify({"sentiment": sentiment})


app.run(
    host="0.0.0.0",
    port=8080,
    debug=True,  # TODO: run in release mode
)
