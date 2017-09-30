import json, sys
from flask import Blueprint, request, g, abort, jsonify

from app import db

from app import app

from app.service_broker.models import SrvInst, SrvBind

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

    return:
        JSON document with details about the
        services offered through this broker
    """
    api_version = request.headers.get('X-Broker-Api-Version')
    if not api_version or not checkversion(api_version):
        raise ServiceBrokerException(409, "Missing or incompatible %s. Expecting version %0.1f or later" % (X_BROKER_API_VERSION_NAME, X_BROKER_API_VERSION))
    return jsonify({"services": vm_services})


@service_broker.route('/v2/service_instances/<instance_id>', methods=['PUT'])
@auth.login_required
def provision(instance_id):
    data = request.get_json()
    if data is None or not data.has_key('service_id'):
        raise ServiceBrokerException(422, "Invalid request data")

    srv_inst = SrvInst(instance_id, data.get('service_id'), data.get("plan_id"), json.dumps(data.get("parameters",{})))
    db.session.add(srv_inst)
    db.session.commit()

    return jsonify({"dashboard_url": app.config['SERVICE_INSTANCE_URI'].format(instance_id=instance_id)}), 201

@service_broker.route('/v2/service_instances/<instance_id>', methods=['DELETE'])
@auth.login_required
def deprovision(instance_id):
    
    #    if not service_instances.has_key(instance_id):
    #        raise ServiceBrokerException(410, "instance not found")

    srv_inst = SrvInst.query.filter_by(srvid = instance_id).first()
    db.session.delete(srv_inst)
    db.session.commit()
    return jsonify({}), 200

@service_broker.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['PUT'])
@auth.login_required
def bind(instance_id, binding_id):
    print >> sys.stderr, request.data
    data = request.get_json()
    if data is None:
        raise ServiceBrokerException(422, "invalid request data")
    

    srv_inst = SrvInst.query.filter_by(srvid = instance_id).first()
    plan = srv_inst.plan
    plan_def = plan_detail[plan]

    srv_bind = SrvBind(instance_id, binding_id, data.get('service_id'),  json.dumps(data.get("parameters")))
    db.session.add(srv_bind)
    db.session.commit()

    return jsonify(
        plan_def
    ), 200

@service_broker.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['DELETE'])
@auth.login_required
def unbind(instance_id, binding_id):
    print >> sys.stderr, request.data

    srv_bind = SrvBind.query.filter_by(bindid = binding_id).filter_by(srvid = instance_id).first()
    db.session.delete(srv_bind)
    db.session.commit()

    return jsonify(
        {}
    ), 200
