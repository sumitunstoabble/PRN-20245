from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["120 per minute"]
)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # Ensure this path is correct
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Train Running Status API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
