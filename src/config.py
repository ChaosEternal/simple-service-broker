import json, os, re

from vcap_config import *

DEBUG = True

SRVCFG  = vcap_extract_cred(VCAP_SERVICE_CONFIG, srvname="srvdb$", tag="mysql")
if SRVCFG is not None:
    SQLALCHEMY_DATABASE_URI = SRVCFG["uri"].split('?')[0]
else:
    SQLALCHEMY_DATABASE_URI = "sqlite:///tmp/xxx.db"

SQLALCHEMY_TRACK_MODIFICATIONS = False

DASHBOARD_PREFIX="/cfbroker"
SERVICE_INSTANCE_URI = "/dashboard/{instance_id}"
