rankt.

Usage:
    rankt init --endpoint
    rankt create <case>
    rankt open <case>  
    rankt top [--size=<s>] <query> [--keywords=<kw>]
    rankt diff (<hits1> <hits2> | --query <query1> <query2>)
    [--side-by-side | --churn] [--keywords=<kw>] [--size=<s>]
    rankt store <type> [-]

Options:
    -h --help           Show this screen.
    -v --version        Show version.
    -e --endpoint       The search endpoint to use.
    -s --size=<size>    Size of hits [default: 3].
    -k --keywords=<kw>  A keywords file [default: keywords].
    -q --query          Query.
    -y --side-by-side   Output diff side by side.
    -c --churn          List churn.

rankt init
----------
create config.yml
touch .rankt - indicate root for finding config by walking up dirs

rankt create <case>
-------------------
creates a case

rankt open <case>
-----------------
cd into cases/<case>

rankt top
---------
rankt top [--size=[defaults config['size']]] <query>

rankt diff
----------
rankt diff <hits1> <hits2> [--side-by-side | --churn]
rankt diff --query <query1> <query2> [--size=n] [--keywords=filename] [--side-by-side | --churn,-x]

examples
========
rankt diff -x <(rankt top -s 3 q1) <(rankt top -s3 q2)
rankt diff -q q1 q2 -y <(cat keywords)

rankt store
-----------
store(type,value) - can be store_es(snapshot,dict) for current use case

examples
========
rankt store snapshot <(rankt top q1)

queries
-------
Every case has a config.yml file with a queries dictionary.
A query can be listed in config['queries'] and be used as a named query.

the config.yml could look like this::

    cat < ./config.yml
    queries_path: queries
    queries:
      baseline:
      title_boost:
        path: queries/with-toggles (optional: defaults to queries_path/title_boost)
        args:
          title_boost: true

The args dictionary is passed to the query template (jinja2).

Additionally, args can be passed in the command line. E.g.,

`rankt top title_boost='{"title_boost":false}'`

In the case of an argument collision, the command line args take precedence.

Queries are looked up in the following order:

config['queries']['<query_name>']
config['queries_path']/<query_name>
./<query_name>
project_root/config['queries']['<query_name>']
project_root/config['queries_path']/<query_name>
project_root/<query_name>

If no matching query is found, an exception is raised.
