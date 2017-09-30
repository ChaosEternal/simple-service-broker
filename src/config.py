import json, os, re

from vcap_config import *

DEBUG = True

SQLALCHEMY_DATABASE_URI = vcap_extract_cred(VCAP_SERVICE_CONFIG, srvname="srvdb$", tag="mysql")["uri"].split('?')[0]

SQLALCHEMY_TRACK_MODIFICATIONS = False
