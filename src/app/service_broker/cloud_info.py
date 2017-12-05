from app import db
from app.service_broker.models import CldInfo
from app.exceptions import *

import urllib.request, urllib.error, urllib.parse, json, uuid, random, array, base64
from urllib2 import urlparse

def normalize_uri(u, scheme="https", include_path = False):
        r = u
        p = urlparse.urlparse(r)
        if len(p.scheme) == 0:
            r = "%s://"%scheme + u
        p = urlparse.urlparse(r)
        if not include_path:
            return "%s://%s"%(p.scheme, p.netloc)
        else:
            return "%s://%s%s"%(p.scheme, p.netloc, p.path)

def make_cld_info(cld_loc_info):
    try:
        r = urllib.request.urlopen(normalize_uri(cld_loc_info, scheme="https", include_path = True))
        cld = json.load(r)
    except Exception as e:
        raise ServiceBrokerException(422,
                                     "Error when fetching %s, reason: %s"%(cld_loc_info, str(e)))
    print(cld)
    cld_oauth_id = str(uuid.uuid4())
    sr = random.SystemRandom()
    cld_oauth_sec = base64.b32encode(array.array("L", [sr.getrandbits(64) for x in range(16)]).tostring())
    return CldInfo(cld_loc_info,                            #  cld_loc_info
                   cld.get("description",            None), #  cld_loc_desc
                   cld.get("name",                   None), #  cld_loc_name
                   cld.get("authorization_endpoint", None), #  cld_authz_edp
                   cld.get("token_endpoint",         None), #  cld_token_edp
                   cld_oauth_id,                            #  cld_oauth_id
                   cld_oauth_sec)                           #  cld_oauth_sec


