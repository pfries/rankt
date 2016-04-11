import os, requests, json
from query import Query
from parser import parse
from store import store

class Snapshot():
    def __init__(self, config):
        query = Query(config['queries_path'])
        query.load_query(config['query'])
        self.query = query
        self.config = config
        self.default_keywords = os.path.join(config['case_path'], 'keywords')

    def snapshot(self):
        self.config['snapshot'] = next_snapshot_id(
                self.config['project'],
                self.config['case'],
                self.config['store_endpoint']
                )

        if self.config.get('keywords'):
            with open(self.config['keywords']) as f:
                for keywords in f:
                    self.snapshot_keywords(keywords)
        elif not sys.stdin.isatty():
            for keywords in sys.stdin:
                self.snapshot_keywords(keywords)
        elif os.path.isfile(self.default_keywords):
            with open(self.default_keywords) as f:
                for keywords in f:
                    self.snapshot_keywords(keywords)
        else:
            raise RuntimeError('Missing keywords.')

    def snapshot_keywords(self, keywords):
        keywords = keywords.strip()
        print('Snapshotting "{}"'.format(keywords))
        kw = keywords.split()
        qs = self.query.render(keywords=kw)
        r = self.query.fetch(self.config['search_url'], self.config.get('optional_params',{}), qs)
        p = parse(r)
        store(keywords, p, self.config)

def get_previous_snapshot(project, case, endpoint):
    query = Query('/home/peter/.rankt/aggs')
    previous = query.load_query('last-snapshot-for-case.json')
    json = query.render(
            project=project,
            case=case
            )
    q = '/'.join([
        endpoint, 
        'snapshot',
        '_search?search_type=count'
        ])
    res = requests.post(q, data=json)
    return res.json()

def next_snapshot_id(project, case, endpoint):
    previous = get_previous_snapshot(project, case, endpoint)
    previous_snapshot_id = 0

    agg_buckets = (previous
        .get('aggregations')
        .get('keywords')
        .get('buckets'))

    if len(agg_buckets):
        previous_snapshot_id = agg_buckets[0].get('snapshots').get('buckets')[0]['key']

    return previous_snapshot_id + 1
