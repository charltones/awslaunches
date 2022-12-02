import feedparser
import pprint
import pydot
from darksolarizedtheme import DarkSolarizedTheme
from graphnode import GraphNode
import re

pp = pprint.PrettyPrinter(indent=2, width=100, compact=True)


def do_substitute_and_or_add(term_hash, k, detail):
    ''' Make some terminology and category substitutions to correct a few
        issues with the tree - like consistency of terms.
        Also correct missing marketing and general tags
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

def do_missing_tags(term_hash, missing):
    ''' Correct for some articles that are missing marketing or product tags
    '''

    missing_tags = {
        'marketing': {
            'general': {
                'amazon-cloudwatch': 'management-and-governance',
                'amazon-vpc': 'networking-and-content-delivery',
                'aws-iot': 'internet-of-things',
                }
        },
        'general': {
            'marketing': {
                'amazon-machine-learning': 'artificial-intelligence-general',
                'artificial-intelligence': 'artificial-intelligence-general',
                'business-productivity': 'business-productivity-general',
                'networking-and-content-delivery': 'networking-general',
                'security-identity-and-compliance': 'security-general',
            }    
        }
    }
    
    replace = missing_tags[missing]
    lookup = list(replace.keys())[0]
    if lookup in term_hash:
        alt = term_hash[lookup][0]
        if lookup in replace and alt in replace[lookup]:
            replacement = replace[lookup][alt]
        else:
            replacement = 'need-replacement'
            print('ERROR: no replacement for:',lookup, alt, term_hash)
    else:
        replacement = 'no-category'
    print('WARNING: replacement made',missing,replacement,term_hash)    
    return [replacement]
    
        
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

    # some of the items don't have marketing and/or general tags
    # so we need to do something more clever here.
    if len(term_hash['marketing']) == 0:
        print("WARNING: no marketing", term_tag)
        term_hash['marketing'] = do_missing_tags(term_hash, 'marketing')
    if (len(term_hash['general']) == 0):
        print("WARNING: no general", term_tag)
        term_hash['general'] = do_missing_tags(term_hash, 'general')
    return term_hash

def select_term(term_hash, category, title):
    keyword_match = {
        'lambda': ['serverless', 'lambda'],
        'emr': ['analytics', 'emr'],
        'compliance': ['compliance']
    }
    if len(term_hash[category])>1:
        if term_hash[category][0]=='aws-govcloud-us':
            term_hash[category].pop(0)
        for kw in keyword_match.keys():
            if re.search(kw, title, re.IGNORECASE):
                for v in keyword_match[kw]:
                    for v2 in term_hash[category]:
                        if re.search(v, v2, re.IGNORECASE):
                            print('WARNING: picking entry based on keyword', v2, kw)
                            return v2
    if len(term_hash[category])>1:
        print('WARNING: discarding entries. Picked 1st from %s for %s' % (term_hash[category], title))
    return term_hash[category][0]
    
def add_hash_to_mindmap(mindmap, term_hash, title):
    # The terms hash often has multiple entries for marketing and general.
    # We're going to simplify for now and just pick the first of each to add to
    # the mindmap since each article should only appear once. Later we could 
    # start looking at analysing the title to see if we can find a best match.
    marketing = mindmap.add_or_insert(select_term(term_hash, 'marketing', title))
    general = marketing.add_or_insert(select_term(term_hash, 'general', title))
    general.add_or_insert(title)

# Download the what's new RSS feed, parse it
rssurl = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"
feed = feedparser.parse(rssurl)

# Loop through all the items in the feed and add them to the mindmap
mindmap = GraphNode.create_root('AWS Launches')
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
print(mindmap.content)
for child in mindmap.children:
    print("+---" + child.content)
    for subchild in child.children:
        print("    +----" + subchild.content)

# For a first attempt at rendering the mindmap I'm using Graphviz
#theme = DarkSolarizedTheme(layout='sfdp', font='arial')
#graph = pydot.Dot(root=mindmap.content, **theme.graph_style)
# Just loop through the tree and add as edges in a Graphviz structure
#for m in mindmap:
#    graph.add_node(pydot.Node(m.content, **theme.node_style(m, 2)))
#    if m.parent:
#        graph.add_edge(pydot.Edge(m.parent.content, m.content, **theme.edge_style(m, 2)))
         
#graph.write_png('out.png')
