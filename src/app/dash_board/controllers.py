import json, sys, urllib.request, urllib.error, urllib.parse, time

from flask import Blueprint, request, g, abort, jsonify, render_template, session, redirect, url_for


from app import db

from app import app, oauth

from app.service_broker.models import CldInfo, SrvcInst, SrvcBind
from app.service_broker.cloud_info import make_cld_info, normalize_uri

from app.exceptions import *

from app.metadata import *

from app.auth import auth

import oauthlib.oauth2

dash_board = Blueprint('dshbrd', __name__, url_prefix="/")

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('dshbrd.status')

class CF_Oauth():
    def __init__(self, oauth):
        self.cld_info = None
        self.cld = None
        self.cf_cc = None
        self.oauth = oauth
        self.token = None
    def update_cld_info(self, instance_id, token = None):
        srvc = SrvcInst.query.filter_by(srvc_inst_id = instance_id).first()
        if srvc is None:
            raise ServiceBrokerException(404, "%s does not exist"%instance_id)
        cld = CldInfo.query.filter_by(cld_loc_info = srvc.cld_info).first()
        if cld is None or cld.cld_authz_edp is None or cld.cld_token_edp is None:
            raise ServiceBrokerException(500, "Database error, cld is None")
        self.cld = cld
        cf_cc = self.oauth.remote_app("CloudFoundry",
                                 register = False,
                                 consumer_key = "%s-%s"%(srvc.srvc_id, cld.cld_oauth_id),
                                 consumer_secret = cld.cld_oauth_sec,
                                 request_token_params = {"scope": "cloud_controller_service_permissions.read openid cloud_controller.read"},
                                 request_token_url = None,
                                 access_token_url = cld.cld_token_edp + "/oauth/token",
                                 authorize_url = cld.cld_authz_edp + "/oauth/authorize"
        )
        self.cf_cc = cf_cc
        self.token = token
        @cf_cc.tokengetter
        def get_cc_oauth_token():
            return session.get('token')

        def make_client(token = None):
            return oauthlib.oauth2.WebApplicationClient(cf_cc.consumer_key, access_token = token)
        cf_cc.make_client = make_client # a bug of flask-oauthlib, this is a dirty fix        

class AuthCC():
    def __init__(self, bp, login = "login", auth = "auth"):
        self.bp = bp
        self.login = login
        self.auth = auth
    def __call__(self, func):
        def check(*args, **argv):
            cf_oauth_ctx.update_cld_info(argv["instance_id"], session.get("token", None))
            if func.__name__ in (self.auth, self.login):
                return func(*args, **argv)
            cur_url = request.url
            instance_id = argv["instance_id"]
            if 'userinfo' not in session or \
            'token' not in session or \
            time.time() + 5 > session["token_expire"]:
                login_url = url_for("%s.%s"%(self.bp, self.login), instance_id = instance_id)
                return redirect(login_url + "?next=%s"%urllib.parse.quote(cur_url))
            return func(*args, **argv)
        check.__name__ = func.__name__
        return check

cf_oauth_ctx = CF_Oauth(oauth)
authcc = AuthCC(bp= "dshbrd")

@dash_board.route("/login/<instance_id>", methods=['GET'])
@authcc
def login(instance_id):
    if 'userinfo' in session:
        session.pop('userinfo')
    r = redirect_url()
    session["next_url"] = r
    cf_cc = cf_oauth_ctx.cf_cc
    return cf_cc.authorize(callback = normalize_uri(app.config["VCAP_APP_URI"]) + url_for("dshbrd.auth", instance_id = instance_id))

@dash_board.route("/auth/<instance_id>", methods=['GET'])
@authcc
def auth(instance_id):
    if request.args.get("error", None) is not None:
        return "Error: %s, <p> Desc: %s"%(request.args.get("error"), request.args.get("error_description","")), 410
    cf_cc = cf_oauth_ctx.cf_cc
    resp = cf_cc.authorized_response()
    if resp is None or "access_token" not in resp:
        return "410 access denied", 410
    session["token"] = resp["access_token"]
    session["token_expire"] = int(resp["expires_in"]) + time.time()

    userinfo = cf_cc.post(cf_oauth_ctx.cld.cld_token_edp + "/userinfo", token = resp["access_token"]).data
    session["userinfo"] = userinfo
    if "next_url" in session:
        next_url = session.pop("next_url")
        return redirect(next_url)
    else:
        return redirect(url_for("dshbrd.status"))

@dash_board.route(app.config["SERVICE_INSTANCE_URI"].format(instance_id='<instance_id>'), methods=['GET'])
@authcc
def dashboard(instance_id):
    userinfo = session["userinfo"]
    srvc = SrvcInst.query.filter_by(srvc_inst_id = instance_id).first()
    cld = CldInfo.query.filter_by(cld_loc_info = srvc.cld_info).first()
    binding = SrvcBind.query.filter_by(srvc_inst_id = instance_id).all()
    srvc_desc = dict([x for x in vm_services if x["id"] == srvc.srvc_id][0])
    srvc_desc["args"] = json.dumps(json.loads(srvc.args), indent=2)
    plan_desc = dict([x for x in srvc_desc["plans"] if x["id"] == srvc.plan][0])
    srvc_desc["plans_json"] = json.dumps(srvc_desc["plans"], indent=2)
    binding_desc = [ {"app": url_for("dshbrd.appinfo", instance_id = instance_id, appid = json.loads(x.args)["app_guid"]),
                      "app_guid": json.loads(x.args)["app_guid"],
                      "args": json.dumps(json.loads(x.args), indent=2)
    } for x in binding ]
    plan_desc.update(plan_detail[plan_desc["id"]])
    return render_template("dashboard.html", cld=cld, srvc= srvc_desc, binding = binding_desc, plan_desc=json.dumps(plan_desc, indent=2), userinfo = userinfo )

@dash_board.route("/appinfo/<instance_id>/<appid>", methods=['GET'])
@authcc
def appinfo(instance_id, appid):
    cf_cc = cf_oauth_ctx.cf_cc
    cld = cf_oauth_ctx.cld
    app_summary_url = "/v2/apps/:guid/summary".replace(":guid",appid)
    app_env_url = "/v2/apps/:guid/env".replace(":guid",appid)
    appinfo = cf_cc.get(normalize_uri(cld.cld_loc_info, scheme="https") + app_summary_url, token = session["token"]).data
    appenv = cf_cc.get(normalize_uri(cld.cld_loc_info, scheme="https") + app_env_url, token = session["token"]).data
    return render_template("appinfo.html", appinfo = json.dumps(appinfo, indent=2), appenv = json.dumps(appenv, indent=2))


@dash_board.route("/status", methods=['GET'])
def status():
    cld = CldInfo
    srvc = SrvcInst
    binding = SrvcBind
    return render_template("status.html", cld=cld, srvc= srvc, binding = binding)
