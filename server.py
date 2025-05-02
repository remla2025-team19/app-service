from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)


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
            version:
              type: string
    """
    # TODO: use lib-version
    return {"version": "0.1.0"}


@app.route("/api/query", methods=["POST"])
def query_model():
    """
    ---
    description: Query the model-service
    parameters:
      - name: query
        in: body
        required: true
        schema:
          type: object
          properties:
            query:
              type: string

    responses:
      200:
        description: The response from the model-service
        schema:
          type: string
    """
    # TODO: query model-service
    query = request.get_json().get("query")
    return jsonify({"sentiment": query})


app.run(
    host="0.0.0.0",
    port=8080,
    debug=True,
)
