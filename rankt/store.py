import requests, json
from hashlib import sha1

def store(keywords, ranked_results, config):
    store_es(keywords, ranked_results, config)

def store_es(keywords, ranked_results, config):
    ''' Store in Elasticsearch '''

    endpoint = config['store_endpoint']
    for d in ranked_results:
        snapshot_params = {
                "project": config['project'],
                "case": config['case'],
                "snapshot": config['snapshot'], 
                "timestamp": config['run_datetime'],
                "keywords": keywords
                }
        d.update(snapshot_params)
        print(d)

        joined_id = '{}{}{}{}{}'.format(config['project'],
                config['case'],keywords,config['snapshot'],d['documentid'])
        
        hashed_id = sha1(joined_id.encode()).hexdigest()
        res = requests.put('/'.join([endpoint, 'snapshot', hashed_id]), data=json.dumps(d))
