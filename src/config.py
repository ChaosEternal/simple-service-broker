import json, os, re
VCAP_APP_CONFIG = json.loads(os.getenv('VCAP_APPLICATION', """{"uris": ["127.0.0.1:8080"]}"""))
VCAP_SERVICE_CONFIG = json.loads(os.getenv('VCAP_SERVICES', """{}"""))
VCAP_APP_URI = VCAP_APP_CONFIG['uris'][0]

SERVICE_INSTANCE_URI = "https://" + VCAP_APP_URI + "/brk/{instance_id}"
SERVICE_BINDING_URI = "https://" + VCAP_APP_URI + "/brk/{instance_id}/{binding_id}"
SERVICE_DASHBOARD_URI = "https://" + VCAP_APP_URI + "/brk/dashboard/{instance_id}"

def vcap_extract_cred(srv_config, dbsrv="srvdb$", dbtag="mysql"):
    for i in srv_config.values():
        for j in i:
            if dbtag in j.get("tags",[]):
                if re.search(dbsrv, j.get("name","")):
                    return j["credentials"]
    raise Exception("FATAL","No database available")
    return None

DEBUG = True

SQLALCHEMY_DATABASE_URI = vcap_extract_cred(VCAP_SERVICE_CONFIG)["uri"].split('?')[0]

SQLALCHEMY_TRACK_MODIFICATIONS = False
