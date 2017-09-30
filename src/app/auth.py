from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
@auth.get_password
def get_pw(username):
    if username == 'adhkadkahdkadhkasha':
        return 'asadasdasd'
    return None
