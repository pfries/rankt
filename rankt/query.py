from jinja2 import Template, Environment, FileSystemLoader
import requests

class Query:
    def __init__(self, queries_config, queries_paths):
        queries = Environment(loader=FileSystemLoader(
            queries_paths, encoding='utf-8'))
        queries.trim_blocks = True
        queries.lstrip_blocks = True
        self.queries = queries

    def load_query(self, query):
        # find query in configs or queries/
        
        self.query = self.env.get_template(query)

    def render(self, **args):
        return self.query.render(args).replace('\n','')

    def fetch(self, endpoint, params, query_string):
        optional_params = '&'.join(['{}={}'.format(k,v) for k,v in params.items()])
        query_string = '&'.join([query_string, optional_params])
        url = '?'.join([endpoint, query_string])
        with open('last-query', 'w') as q:
            q.write(url)
        return requests.get(url)

