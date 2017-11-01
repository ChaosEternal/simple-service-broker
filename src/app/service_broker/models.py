from app import db

class CldInfo(db.Model):
    """Cloud Info"""
    __tablename__ = "cld_info"
    cld_loc_info  = db.Column(db.String(255), nullable=False, primary_key=True)
    cld_loc_desc  = db.Column(db.TEXT())
    cld_loc_name  = db.Column(db.TEXT())
    cld_authz_edp = db.Column(db.TEXT())
    cld_token_edp = db.Column(db.TEXT())
    cld_oauth_id  = db.Column(db.String(128))
    cld_oauth_sec = db.Column(db.TEXT())
    def __init__(self
                 ,cld_loc_info
                 ,cld_loc_desc
                 ,cld_loc_name
                 ,cld_authz_edp
                 ,cld_token_edp
                 ,cld_oauth_id
                 ,cld_oauth_sec):
        self.cld_loc_info   = cld_loc_info
        self.cld_loc_desc   = cld_loc_desc
        self.cld_loc_name   = cld_loc_name
        self.cld_authz_edp  = cld_authz_edp
        self.cld_token_edp  = cld_token_edp
        self.cld_oauth_id   = cld_oauth_id
        self.cld_oauth_sec  = cld_oauth_sec
    def __repr__(self):
        return "<CldInfo %s>"%self.cld_loc_info

class SrvcInst(db.Model):
    """Service Instances"""
    __tablename__ = "srvc_inst"
    srvc_inst_id  = db.Column(db.String(128), nullable=False, primary_key=True)
    srvc_id       = db.Column(db.String(128), nullable=False)
    plan          = db.Column(db.String(128), nullable=False)
    args          = db.Column(db.TEXT())
    cld_info      = db.Column(db.String(255))

    def __init__(self
                 ,srvc_inst_id
                 ,srvc_id
                 ,plan
                 ,args
                 ,cld_info
    ):
        self.srvc_inst_id  = srvc_inst_id
        self.srvc_id       = srvc_id
        self.plan          = plan
        self.args          = args
        self.cld_info      = cld_info
    def __repr__(self):
        return "<SrvInst %s>"%self.srvid

class SrvcBind(db.Model):
    """Service Binding"""
    __tablename__ = "srvc_bind"
    bind_id       = db.Column(db.String(128), nullable=False, primary_key=True)
    srvc_inst_id  = db.Column(db.String(128), nullable=False, primary_key=True)
    srvc_id       = db.Column(db.String(128), nullable=False)
    args          = db.Column(db.TEXT())

    def __init__(self
                 ,bind_id
                 ,srvc_inst_id
                 ,srvc_id
                 ,args):
        self.bind_id      = bind_id
        self.srvc_inst_id = srvc_inst_id
        self.srvc_id      = srvc_id
        self.args         = args
    def __repr__(self):
        return "<Bind %s of %s>"%(self.bindid, self.srvid)
