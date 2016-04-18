import argparse, os

def _load_configs(args):
    '''
    Load the config files for the current context.
    '''
    config = {}
    master_config = os.path.join(
            os.path.expanduser('~'),
            '.rankt/config.yml')
    # first load the master config
    with open(master_config) as mc:
        config = yaml.load(mc)

    # find the project config
    cwd = os.getcwd()
    while not os.path.exists('.rankt'):
        os.chdir('..')
    # load the project config
    with open('config.yml') as c:
        config.update(yaml.load(c))

    # back to start and check for local config
    os.chdir(cwd)
    if os.path.exists('config.yml'):
        with open('config.yml') as c:
            config.update(yaml.load(c))

    config.update(vars(args))
    return config

def init(args):
    '''
    Initialize a rankt project.
    '''
    if os.path.exists('.rankt'):
        raise RuntimeError('Directory already initialized.')

    config = _load_configs(args)

    cases_path = config['cases_path'] or 'cases'
    try:
        os.makedirs(cases_path)
    except OSError:
        raise RuntimeError('Found cases. Aborting.')

    project_config = {
            'project_name': args.project_name,
            'search_url': args.search_url
            }
    
    with open('config.yml', 'w') as c:
        c.write(yaml.dump(project_config, default_flow_style=False))

def create():
    '''
    Create a rankt case.
    '''
    pass

def open():
    '''
    Open a rankt case.
    '''
    pass

def top():
    '''
    Get the top results for a query given a list of keywords.
    '''
    pass

def store():
    '''
    Store an object for reporting.
    '''
    pass

def diff():
    '''
    Compare the positions of search results for the same keywords.
    '''
    pass

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser('init', help='initialize a project')
    init_parser.add_argument('--search-url', '-u', required=True)
    init_parser.add_argument('project', nargs='?',
            default=os.path.basename(os.getcwd()), 
            help='name of the project (default: pwd)'
            )
    init_parser.set_defaults(func=init)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
