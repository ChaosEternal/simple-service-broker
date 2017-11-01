from flask import Flask, jsonify, session
from flask_sqlalchemy import SQLAlchemy

from app.exceptions import ServiceBrokerException
from flask_oauthlib.client import OAuth

import os

app = Flask(__name__)


app.config.from_object('config')
app.secret_key = os.urandom(24)
oauth = OAuth(app)
db = SQLAlchemy(app)

@app.errorhandler(ServiceBrokerException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

from app.service_broker.controllers import service_broker as service_broker_module
from app.dash_board.controllers import dash_board as dash_board_module

app.register_blueprint(service_broker_module, url_prefix='')
app.register_blueprint(dash_board_module, url_prefix=app.config["DASHBOARD_PREFIX"])

#db.create_all()
