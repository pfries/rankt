def parse(response):
    return parse_solr(response)

def parse_solr(response):
    solr_response = response.json()
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
        positions.append(p)
    return positions
