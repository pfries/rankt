def parse(response, store_fields={}):
    return parse_solr(response, store_fields)

def parse_solr(response, store_fields={}):
    solr_response = response.json()
    if not solr_response.get('response'):
        raise RuntimeError(str(solr_response))
    if not solr_response.get('response').get('docs'):
        return []
    docs = solr_response['response']['docs']
    debug = solr_response['debug']
    parsed_query = debug['parsedquery']

    positions = []
    for idx, doc in enumerate(docs):
        p = {
                "doc_position": idx+1, 
                "documentid": doc['documentid'], 
                "doc_score": doc['score'],
                "doc_explain": debug['explain'][doc['documentid']],
                "parsed_query": parsed_query
            }
        if store_fields:
            for k,v in store_fields.items():
                p[k] = doc[v]

        positions.append(p)
    return positions
