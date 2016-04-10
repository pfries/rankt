class Snapshot():
    def __init__(self, config):
        query = Query(config['queries_path'])
        query.load_query(config['query'])
        self.query = query
        self.config = config
        self.default_keywords = os.path.join(config['case_path'], 'keywords')

    def snapshot(self):
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
        store(keywords, p, 
                self.config['snapshot'], 
                self.config['store_endpoint'],
                self.config['run_datetime'])
