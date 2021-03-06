import os, requests, json
from collections import OrderedDict
from itertools import zip_longest
from sys import stdin, stdout
from query import Query
from parser import parse
from store import store
from hashlib import sha1

class Snapshot():
    def __init__(self, config):
        query = Query(config['queries_path'])
        self.query = query
        self.config = config
        self.default_keywords = os.path.join(config['case_path'], 'keywords')

    def snapshot(self):
        self.config['snapshot'] = next_snapshot_id(
                self.config['project'],
                self.config['case'],
                self.config['store_endpoint']
                )

        ss = []
        if self.config.get('keywords'):
            for keywords in self.config['keywords']:
                s = self.snapshot_keywords(keywords)
                if len(s):
                    ss.append(s)
        else:
            raise RuntimeError('Missing keywords.')
        return ss

    def snapshot_keywords(self, keywords):
        try:
            keywords = keywords.strip()
            kw = keywords.split()
            queries = []
            for q in self.config['query']:
                self.query.load_query(q['query_template'])
                query_args = {
                        "keywords": kw
                        }
                query_args.update(q.get('query_args',{}))
                qs = self.query.render(**query_args)
                queries.append(qs)
            final_query = '&'.join(queries)

            opt_params = self.config.get('optional_params',{})
            if(self.config.get('size')):
                opt_params['rows'] = self.config['size']
            r = self.query.fetch(self.config['search_url'], opt_params, final_query)
            p = parse(r, self.config.get('store_fields'))
            store_endpoint = self.config['store_endpoint']
            for d in p:
                snapshot_params = {
                        "project": self.config['project'],
                        "case": self.config['case'],
                        "query": str(self.config['query']),
                        "snapshot": self.config['snapshot'], 
                        "timestamp": self.config['run_datetime'],
                        "keywords": keywords
                        }

                d.update(snapshot_params)
            return p
        except Exception as ex:
            print(keywords)
            raise

def get_snapshot_aggregation(project, case, size, endpoint, page_size=10):
    query = Query('/home/peter/.rankt/aggs')
    previous = query.load_query('keywords-by-snapshot.json')
    json = query.render(
            project=project,
            case=case,
            size=size,
            page_size=page_size
            )
    q = '/'.join([
        endpoint, 
        'snapshot',
        '_search?search_type=count'
        ])
    res = requests.post(q, data=json)
    return res.json()

def get_previous_snapshot(project, case, endpoint):
    return get_snapshot_aggregation(project, case, 1, endpoint)

def parse_snapshots(agg):
    buckets = (agg
        .get('aggregations')
        .get('snapshots')
        .get('buckets'))

    snapshots = OrderedDict()
    for snapshot in buckets:
        snapshot_id = snapshot['key']
        snapshots[snapshot_id] = {}
        keywords = snapshot['keywords']['buckets']
        kw_dict = {}
        for k in keywords:
            kw = k['key']
            hits = k['doc_positions']['hits']['hits']
            positions = []
            for h in hits:
                positions.append((h['_source']['doc_position'],h['_source']['documentid']))
            kw_dict[kw] = positions
        snapshots[snapshot_id] = kw_dict

    return snapshots


def next_snapshot_id(project, case, endpoint):
    previous = get_previous_snapshot(project, case, endpoint)
    snapshots = parse_snapshots(previous)
    previous_snapshot_id = 0

    if len(snapshots):
        previous_snapshot_id = list(snapshots)[0]

    return previous_snapshot_id + 1

def diff_last_two(project, case, endpoint):
    agg = get_snapshot_aggregation(project, case, 2, endpoint)
    snapshots = parse_snapshots(agg)
    latest,previous = tuple(list(snapshots.values()))
    return calculate_churn(previous, latest)


def calculate_churn(results1, results2):
    ''' Churn is a measure of how different the two results are.'''
    churn_report = {
            'churn_score': 0.0,
            'keywords': {}
            }
    for keyword in results1.keys():
        a = OrderedDict(results1[keyword])
        b = OrderedDict(results2.get(keyword, []))
        diff = []
        for i, j in zip_longest(a.items(), b.items()):
            if i != j:
                diff.append(i)
        set_diff = len(set(a) - set(b)) or 1
        kw_churn_score = (set_diff * (len(diff) or 1))
        churn_report['keywords'][keyword] = {
                'positional_changes': diff,
                'set_difference': set_diff,
                'churn_score': kw_churn_score
                }
        churn_report['churn_score'] += kw_churn_score
    return churn_report
