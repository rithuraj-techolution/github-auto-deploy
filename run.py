"""Flask Backend Server"""
from flask import Flask
from flask_cors import CORS
from core_apis.view import api

from core_apis.view import namens
from core_apis.view import name



def create_app(flask_api):
    """
    Initiate Flask App.
    Args:
        flask_api (object): An instance of the Flask API.
    Returns:
        object: The initialized Flask app.
    """
    flask_app = Flask(__name__)
    CORS(flask_app)

    # Register blueprints
    flask_app.register_blueprint(name)
    flask_api.init_app(flask_app)

    flask_api.add_namespace(namens)

    return flask_app


app = create_app(api)

if __name__ == '__main__':
    app.run("0.0.0.0", port=5005, debug=False, use_reloader=False)

# 10th april 2024
# 4 pm around (4: 08 pm approx)
