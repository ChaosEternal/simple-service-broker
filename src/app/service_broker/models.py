from app import db

class SrvInst(db.Model):
    """Service Instances"""
    __tablename__ = "srv_inst"
    srvid = db.Column(db.String(128), nullable=False, primary_key=True)
    srv = db.Column(db.String(128), nullable=False)
    plan = db.Column(db.String(128), nullable=False)
    args = db.Column(db.String(1024))
    
    def __init__(self, srvid,srv, plan, args):
        self.srvid = srvid
        self.srv = srv
        self.plan = plan
        self.args = args
    def __repr__(self):
        return "<SrvInst %s>"%self.srvid

class SrvBind(db.Model):
    """Service Binding"""
    __tablename__ = "srv_bind"
    bindid = db.Column(db.String(128), nullable=False, primary_key=True)
    srvid = db.Column(db.String(128), nullable=False, primary_key=True)
    srv = db.Column(db.String(128), nullable=False)
    args = db.Column(db.String(1024))

    def __init__(self, srvid, bindid, srv, args):
        self.srvid = srvid
        self.bindid = bindid
        self.srv = srv
        self.args = args

    def __repr__(self):
        return "<Bind %s of %s>"%(self.bindid, self.srvid)
