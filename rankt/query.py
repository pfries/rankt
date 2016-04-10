from jinja2 import Template, Environment, FileSystemLoader
import requests

class Query:
    def __init__(self, queries_path):
        env = Environment(loader=FileSystemLoader(
            queries_path, encoding='utf-8'))
        env.trim_blocks = True
        env.lstrip_blocks = True
        self.env = env

    def load_query(self, query):
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

