import os, requests, json
from collections import OrderedDict
from itertools import zip_longest
from sys import stdin
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
        elif not stdin.isatty():
            for keywords in stdin:
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

def get_snapshot_aggregation(project, case, size, endpoint):
    query = Query('/home/peter/.rankt/aggs')
    previous = query.load_query('keywords-by-snapshot.json')
    json = query.render(
            project=project,
            case=case,
            size=size
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
    results2.pop('manufacturing', None)
    results2['sporting goods'] = list(reversed(results2['sporting goods']))
    results2['elisa'].pop(1)
    results2['property manager'][0], results2['property manager'][1] = results2['property manager'][1], results2['property manager'][0]

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
        kw_churn_score = set_diff * (len(diff) or 1) * .1
        churn_report['keywords'][keyword] = {
                'positional_changes': diff,
                'set_difference': set_diff,
                'churn_score': kw_churn_score
                }
        churn_report['churn_score'] += kw_churn_score
    return churn_report
