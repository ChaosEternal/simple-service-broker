import json, sys

from flask import Blueprint, request, g, abort, jsonify

from app import db

from app import app

from app.service_broker.models import CldInfo, SrvcInst, SrvcBind
from app.service_broker.cloud_info import make_cld_info, normalize_uri

from app.exceptions import *

from app.metadata import *

from app.auth import auth

service_broker = Blueprint('srvbrk', __name__, url_prefix="/")

@service_broker.route('/v2/catalog', methods=['GET'])
@auth.login_required
def catalog():
    """
    Return the catalog of services handled
    by this broker
    
    GET /v2/catalog:
    
    HEADER:
        X-Broker-Api-Version: <version>
        X-Api-Info-Location: cloud-info-location
    return:
        JSON document with details about the
        services offered through this broker
    """
    api_version = request.headers.get('X-Broker-Api-Version')
    cloud_api_location = request.headers.get('X-Api-Info-Location', None)
    cld = None
    if cloud_api_location is not None:
        cld = make_cld_info(cloud_api_location)
        cld_exists = CldInfo.query.filter_by(cld_loc_info = cloud_api_location).first()
        if cld_exists is not None:
            db.session.delete(cld_exists)
            db.session.commit()
        db.session.add(cld)
        db.session.commit()

    if not api_version or not checkversion(api_version):
        raise ServiceBrokerException(409, "Missing or incompatible %s. Expecting version %0.1f or later" % (X_BROKER_API_VERSION_NAME, X_BROKER_API_VERSION))

    def patch_service(s, cld):
        rs = dict(s)
        if cld is not None:
            rs["dashboard_client"] = {"id": "%s-%s"%(rs["id"], cld.cld_oauth_id),
                                      "secret": cld.cld_oauth_sec,
                                      "redirect_uri": normalize_uri(app.config["VCAP_APP_URI"])}
        return rs
    return jsonify({"services": [patch_service(x, cld) for x  in vm_services]})


@service_broker.route('/v2/service_instances/<instance_id>', methods=['PUT'])
@auth.login_required
def provision(instance_id):
    data = request.get_json()
    if data is None or not data.has_key('service_id'):
        raise ServiceBrokerException(422, "Invalid request data")

    cloud_api_location = request.headers.get('X-Api-Info-Location', None)
    cld_info = None
    if cloud_api_location is not None:
        cld = CldInfo.query.filter_by(cld_loc_info = cloud_api_location).first()
        if cld is not None:
            cld_info = cld.cld_loc_info

    srvc_inst = SrvcInst(instance_id, data.get('service_id'), data.get("plan_id"), json.dumps(data), cld_info)
    db.session.add(srvc_inst)
    db.session.commit()

    return jsonify({"dashboard_url": normalize_uri(app.config["VCAP_APP_URI"]) +
                    app.config['DASHBOARD_PREFIX'] +
                    app.config['SERVICE_INSTANCE_URI'].format(instance_id=instance_id)}), 201

@service_broker.route('/v2/service_instances/<instance_id>', methods=['DELETE'])
@auth.login_required
def deprovision(instance_id):
    
    #    if not service_instances.has_key(instance_id):
    #        raise ServiceBrokerException(410, "instance not found")

    srvc_inst = SrvcInst.query.filter_by(srvc_inst_id = instance_id).first()
    db.session.delete(srvc_inst)
    db.session.commit()
    return jsonify({}), 200

@service_broker.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['PUT'])
@auth.login_required
def bind(instance_id, binding_id):
    print >> sys.stderr, request.data
    data = request.get_json()
    if data is None:
        raise ServiceBrokerException(422, "invalid request data")
    

    srvc_inst = SrvcInst.query.filter_by(srvc_inst_id = instance_id).first()
    plan = srvc_inst.plan
    plan_def = plan_detail[plan]

    srvc_bind = SrvcBind(binding_id, instance_id, data.get('service_id'),  json.dumps(data))
    db.session.add(srvc_bind)
    db.session.commit()

    return jsonify(
        plan_def
    ), 200

@service_broker.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['DELETE'])
@auth.login_required
def unbind(instance_id, binding_id):
    print >> sys.stderr, request.data

    srvc_bind = SrvcBind.query.filter_by(bind_id = binding_id).filter_by(srvc_inst_id = instance_id).first()
    db.session.delete(srvc_bind)
    db.session.commit()

    return jsonify(
        {}
    ), 200
