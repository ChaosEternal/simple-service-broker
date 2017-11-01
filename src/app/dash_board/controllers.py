import json, sys

from flask import Blueprint, request, g, abort, jsonify, render_template, session, redirect, url_for


from app import db

from app import app, oauth

from app.service_broker.models import CldInfo, SrvcInst, SrvcBind
from app.service_broker.cloud_info import make_cld_info, normalize_uri

from app.exceptions import *

from app.metadata import *

from app.auth import auth

dash_board = Blueprint('dshbrd', __name__, url_prefix="/")

@dash_board.route(app.config["SERVICE_INSTANCE_URI"].format(instance_id='<instance_id>'), methods=['GET'])
def dashboard(instance_id):
    if 'username' not in session:
        srvc = SrvcInst.query.filter_by(srvc_inst_id = instance_id).first()
        if srvc is None:
            return  "404: %s does not exist"%instance_id, 404
        if srvc.cld_info is None:
            return "No cloud info, dash board is not served", 404
        
        cld = CldInfo.query.filter_by(cld_loc_info = srvc.cld_info).first()
        if cld is None or cld.cld_authz_edp is None or cld.cld_token_edp is None:
            return "Database error, cld is None", 500
        cf_cc = oauth.remote_app("CloudFoundry",
                                 register = False,
                                 consumer_key = "%s-%s"%(srvc.srvc_id, cld.cld_oauth_id),
                                 consumer_secret = cld.cld_oauth_sec,
                                 request_token_params = {"scope": "cloud_controller_service_permissions.read, openid, cloud_controller.read"},
                                 request_token_url = None,
                                 access_token_url = cld.cld_token_edp + "/oauth/token",
                                 authorize_url = cld.cld_authz_edp + "/oauth/authorize"

        )
        session["service_inst"] = instance_id
        return cf_cc.authorize(callback = normalize_uri(app.config["VCAP_APP_URI"]) + url_for("dshbrd.auth"))
    cld = CldInfo
    srvc = SrvcInst
    binding = SrvcBind
    return render_template("dashboard.html", cld=cld, srvc= srvc, binding = binding)

@dash_board.route("/status", methods=['GET'])
def status():
    cld = CldInfo
    srvc = SrvcInst
    binding = SrvcBind
    return render_template("status.html", cld=cld, srvc= srvc, binding = binding)
    
@dash_board.route("/auth", methods=['GET'])
def auth():
    srvc = SrvcInst.query.filter_by(srvc_inst_id = session["service_inst"]).first()
    if srvc is None:
        return  "404: %s does not exist"%instance_id, 404
    if srvc.cld_info is None:
        return "No cloud info, dash board is not served", 404

    cld = CldInfo.query.filter_by(cld_loc_info = srvc.cld_info).first()
    if cld is None or cld.cld_authz_edp is None or cld.cld_token_edp is None:
        return "Database error, cld is None", 500
    cf_cc = oauth.remote_app("CloudFoundry",
                             register = False,
                             consumer_key = "%s-%s"%(srvc.srvc_id, cld.cld_oauth_id),
                             consumer_secret = cld.cld_oauth_sec,
                             request_token_params = {"scope": "cloud_controller_service_permissions.read, openid, cloud_controller.read"},
                             request_token_url = None,
                             access_token_url = cld.cld_token_edp + "/oauth/token",
                             authorize_url = cld.cld_authz_edp + "/oauth/authorize"
    )

    login_info = cf_cc.authorized_response()
    if login_info is None:
        return "410 access denied", 410
    return "%s"%login_info
