
# Necessary Imports
import pytest
from flask import Flask
from flask_cors import CORS
from core_apis.view import api, namens, name
from run import create_app

# Mocking the Flask and CORS classes
Flask = pytest.mock.Mock(spec=Flask)
CORS = pytest.mock.Mock(spec=CORS)

# Test cases generated
def test_create_app():
    # Test case for the create_app function
    flask_app = create_app(api)
    Flask.assert_called_once_with(__name__)
    CORS.assert_called_once_with(flask_app)
    flask_app.register_blueprint.assert_called_once_with(name)
    api.init_app.assert_called_once_with(flask_app)
    api.add_namespace.assert_called_once_with(namens)
    assert flask_app == create_app(api)
