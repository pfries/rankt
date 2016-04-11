import os, requests, json
from collections import OrderedDict
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

    snapshots = {}
    for snapshot in buckets:
        snapshot_id = snapshot['key']
        snapshots[snapshot_id] = {}
        keywords = snapshot['keywords']['buckets']
        for k in keywords:
            kw = k['key']
            hits = k['doc_positions']['hits']['hits']
            positions = []
            for h in hits:
                positions.append((h['_source']['doc_position'],h['_source']['documentid']))
            snapshots[snapshot_id][kw] = OrderedDict(positions)

    return snapshots


def next_snapshot_id(project, case, endpoint):
    previous = get_previous_snapshot(project, case, endpoint)
    snapshots = parse_snapshots(previous)
    previous_snapshot_id = 0

    if len(snapshots):
        for k in snapshots:
            previous_snapshot_id = k

    return previous_snapshot_id + 1

def diff_last_two(project, case, endpoint):
    agg = get_snapshot_aggregation(project, case, 2, endpoint)
    # build comparable sets

def calculate_churn(results1, results2):
    ''' Churn is a measure of how different the two results are.'''
    a = OrderedDict()
    b = OrderedDict()
    diff = []
    for i, j in zip(a.items(), b.items()):
        if i == j:
            diff.append(i)
