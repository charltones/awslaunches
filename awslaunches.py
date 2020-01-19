import feedparser
import pprint
import pydot

pp = pprint.PrettyPrinter(indent=2, width=100, compact=True)


def do_substitute_and_or_add(term_hash, k, detail):
    ''' Make some terminology and category substitutions to correct a few
        issues with the tree - like consistency of terms.
    '''
    
    substitutions = {
        'marketing': {
            'marchitecture': {
                'applications': ('marketing', 'application-services'),
                'management-tools': ('marketing', 'management-and-governance'),
                'developers': ('marketing', 'developer-tools')
            }
        },
        'general': {
            'products': {
                'amazon-machine-learning': ('marketing', 'artificial-intelligence'),
                'amazon-ec2-systems-manager': ('general', 'aws-systems-manager'),
            }
            
        }
    }

    subk = k
    subd1 = detail[1]
    if k in substitutions:
        if detail[0] in substitutions[k]:
            if detail[1] in substitutions[k][detail[0]]:
                (subk, subd1) = substitutions[k][detail[0]][detail[1]]
    term_hash[subk].append(subd1)
        
def parse_termtag(term_tag):
    ''' The AWS what's new blog RSS feed contains a useful tag element called
        'terms' which is roughly a list of categories. Generally there is a 
        high level category under 'marketing' that starts with 'marchitecture/'
        and a lower level / product category under 'general' that starts with
        'products/'. There are a few exceptions and inconsistencies that need
        some fettling but generally it works.
        This function parses the entire terms tag and returns the result as a 
        hash split out into those high and low level categories.
    '''
    
    term_hash = {'marketing': [], 'general': [], 'other': []}
    terms = [tuple(a.split(':')) for a in term_tag.split(',')]
    for (k,v) in terms:
        detail = v.split('/')
        if k=='marketing':
            if detail[0]=='marchitecture':
                do_substitute_and_or_add(term_hash, k, detail)
            else:
                print('WARNING: non marchitecture: ', detail[0], detail[1])
        elif k=='general':
            if detail[0]=='products':
                do_substitute_and_or_add(term_hash, k, detail)
            else:
                print('WARNING: non products: ', detail[0], detail[1])
        else:
            print('WARNING: other: ', k, v)

    # todo: some of the items don't have marketing and/or general tags
    #       so we need to do something more clever here.
    if len(term_hash['marketing']) == 0:
        print("ERROR: no marketing", term_tag)
        term_hash['marketing'] = ['no_marketing']
    if (len(term_hash['general']) == 0):
        print("ERROR: no general", term_tag)
        term_hash['general'] = ['no_general']
    return term_hash

def add_node(tree_node, title, node_type = 'hash'):
    ''' We're going to represent the mind map as a top level hash, representing
        the root node and its edges. Each value in the hash is a mid level node
        which also is a hash that returns a list of articles.
        So tree['a']['b'] is a list of articles within
        the hierarchy root->a->b.
        We therefore have both hashes and lists in the tree hence this function
        to add each one accordingly.
    '''
    
    if node_type == 'list':
        blank_node = []
    else:
        blank_node = {}
    if title not in tree_node:
        tree_node[title] = blank_node
    return tree_node[title]
    
def add_hash_to_mindmap(mindmap, term_hash, title):
    # The terms hash often has multiple entries for marketing and general.
    # We're going to simplify for now and just pick the first of each to add to
    # the mindmap since each article should only appear once. Later we could 
    # start looking at analysing the title to see if we can find a best match.
    node = add_node(mindmap, term_hash['marketing'][0])
    node = add_node(node, term_hash['general'][0], node_type='list')
    node.append(title)

# Download the what's new RSS feed, parse it
rssurl = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"
feed = feedparser.parse(rssurl)

# Loop through all the items in the feed and add them to the mindmap
mindmap = {}
for item in feed['items']:
    tags = item['tags']
    if tags:
        term_hash = parse_termtag(tags[0]['term'])
        title = item['title']
        pub = item['published_parsed']
        add_hash_to_mindmap(mindmap, term_hash, title)
    else:
        print("ERROR: article with no tags", title)
        # todo - do something about items that don't have tags!
        pass

# Let's have a look at the output
pp.pprint(mindmap)

# For a first attempt at rendering the mindmap I'm using Graphviz
root = 'AWS Launches'
graph = pydot.Dot(graph_type='digraph', rankdir='LR')
# Just loop through the tree and add as edges in a Graphviz structure
for m in mindmap.keys():
    graph.add_edge(pydot.Edge(root, m))
    for p in mindmap[m].keys():
        graph.add_edge(pydot.Edge(m, p))
        for s in mindmap[m][p]:
            graph.add_edge(pydot.Edge(p, s))            
graph.write_png('out.png')
