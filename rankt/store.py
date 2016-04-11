import requests, json
from hashlib import sha1

def store(endpoint, document):
    store_es(endpoint, document)

def store_es(endpoint, document):
    ''' Store in Elasticsearch '''
    res = requests.put(endpoint, data=json.dumps(document))
