X_BROKER_API_VERSION = (2, 3)
X_BROKER_API_VERSION_NAME = 'X-Broker-Api-Version'

redis_uat_plan = {
          "id": "9502c1d8-61b4-4995-a711-13d21ccd3a51",
          "name": "TEST Static",
          "description": "Test redis settings." }
db2_uat_plan = {
          "id": "52fe6df7-2cb4-476d-8298-040d5efdf663",
          "name": "TEST Static",
          "description": "Test mysql settings." }
# services
vm_services = [{'id': '393eced5-d9d1-4fa9-85f5-d22a4e16098d',
                 'name': 'simple-redis-service',
                 'description': 'Simple Static Redis Service',
                 'bindable': True,
                 'tags': ['redis'],
                 'metadata': {"longDescription": "Simple Static Redis Service"},
                 'plans': [redis_uat_plan]},
               {'id': '0a41a1db-8557-4f1b-8448-950ad15c7d16',
                 'name': 'simple-db2-service',
                 'description': 'Simle MySQL Service ',
                 'bindable': True,
                 'tags': ['mysql','relational'],
                 'metadata': {"longDescription": "Simple Statis Mysql Service"},
                 'plans': [db2_uat_plan]}
]

plan_detail = {"9502c1d8-61b4-4995-a711-13d21ccd3a51":
               {
                   "credentials" : {
                       "cluster": [
                           {'host': '172.18.11.11', 'port': 7012},
                           {'host': '172.18.11.12', 'port': 7013},
                           {'host': '172.18.11.13', 'port': 7014}
                       ]
                   }
               },
               "52fe6df7-2cb4-476d-8298-040d5efdf663": {
                   "credentials": {
                       "uri" : "mysql://eqkl3ya8:l9vglo0t@172.18.11.21:3306/cf_a632a7da-5aa8-4676-bbd0-1d786bf77975?reconnect=true",
                       "name" : "cf_a632a7da-5aa8-4676-bbd0-1d786bf77975",
                       "port" : 3306,
                       "username" : "eqkl3ya8",
                       "jdbcUrl" : "jdbc:mysql://192.168.8.210:3306/cf_a632a7da-5aa8-4676-bbd0-1d786bf77975?user=eqkl3ya8&password=l9vglo0t",
                       "password" : "l9vglo0t",
                       "hostname" : "172.18.11.21"
                   }
               }
}


def checkversion(x):
    client_version = [int(y) for y in  x.split('.')]
    comp = [ y - x for x,y in zip(X_BROKER_API_VERSION, client_version) ]
    if comp[0] > 0:
        return True
    if comp[0] <0:
        return False
    if comp[1] <0:
        return False
    else:
        return True
    return false
