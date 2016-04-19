from parser import parse
import requests
from jinja2 import Template, Environment, FileSystemLoader

class Top():
    def __init__(self, context):
        self.context = context

    def _fetch(self, endpoint, params, query_string):
        optional_params = '&'.join(['{}={}'.format(k,v) for k,v in params.items()])
        query_string = '&'.join([query_string, optional_params])
        url = '?'.join([endpoint, query_string])
        with open('last-query', 'w') as q:
            q.write(url)
        return requests.get(url)

    def _load(self, query):
        try:
            if self.context.get('queries'):
                query_config = self.context['queries']
                if query_config.get(query) and query_config[query].get('path'):
                    with open(query_config[query]['path']) as t:
                        return Template(t.read())

            # otherwise, load from known paths
            lookup_paths = 'queries'
            loader = FileSystemLoader(lookup_paths, encoding='utf-8')
            env = Environment(loader=loader)
            env.trim_blocks = True
            env.lstrip_blocks = True
            return env.get_template(query)
        except:
            raise RuntimeError('Unable to load query template for {}.'
                    .format(query))

    def _get_query_args(self, query):
        if self.context.get('queries'):
            query_config = self.context['queries']
            if query_config.get(query) and query_config[query].get('args'):
                return query_config[query]['args']
        return {}

    def top(self, query, keywords=[]):
        top_hits = []
        qt = self._load(query)
        q_args = self._get_query_args(query)

        opt_params = self.context.get('optional_params',{})
        if(self.context.get('size')):
            opt_params['rows'] = self.context['size']

        for kw in keywords:
            kws = kw.strip().split()
            q_args['keywords'] = kws
            q = qt.render(**q_args).replace('\n','')
            r = self._fetch(self.context['search_url'], opt_params, q)
            p = parse(r, self.context.get('parse_fields'))
            for d in p:
                context_params = {
                        "project": self.context['project'],
                        "case": self.context['case'],
                        "query": str({'name': query,'args':q_args}),
                        "keywords": kw.strip()
                        }

                d.update(context_params)
            top_hits.append(p)
        return top_hits 

