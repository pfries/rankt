Intro
=====

rankt is a suite of tools for tracking and testing search relevancy

# Setup
rankt requires Python 3

## Create a virtual environment
```pyvenv venv```
## Install dependencies
```pip install -r requirements.txt```

Commands
========

Initializing a new project
--------------------------

`rankt init -h` for more info.

Basic example:

rankt init --search-url [the url of your solr core select handler]

Start a new case
----------------

`rankt create -h` for more info.

A case is used to organize relevancy tuning.

rankt create [name of case, e.g., top100_keywords]

You will now have a cases/top100_keywords/queries path for your query
experiments.

Queries support jinja2 template syntax.

Snapshot document positions at time T
-------------------------------------

`rankt snapshot -h` for more info.

Basic example:

rankt snapshot [case name] --query [query template filename] --keywords [path
to keywords file]

This will save the document at each position for each keyword in --keywords
file.

