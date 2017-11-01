import json, sys

from flask import Blueprint, request, g, abort, jsonify, render_template

from app import db

from app import app

from app.service_broker.models import CldInfo, SrvcInst, SrvcBind
from app.service_broker.cloud_info import make_cld_info, normalize_uri

from app.exceptions import *

from app.metadata import *

from app.auth import auth

dash_board = Blueprint('dshbrd', __name__, url_prefix="/")

@dash_board.route(app.config["SERVICE_INSTANCE_URI"].format(instance_id='<instance_id>'), methods=['GET'])
def dashboard(instance_id):
    cld = CldInfo
    srvc = SrvcInst
    binding = SrvcBind
    return render_template("dashboard.html", cld=cld, srvc= srvc, binding = binding)

@dasg_board.route("/status", methods=['GET'])
def status():
    cld = CldInfo
    srvc = SrvcInst
    binding = SrvcBind
    return render_template("status.html", cld=cld, srvc= srvc, binding = binding)
    
