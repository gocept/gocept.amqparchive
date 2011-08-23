# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree


# XXX tests are missing, see #9501


def jsonify(xmltext):
    return to_dict(lxml.etree.fromstring(xmltext))


def simplify_dict(data):
    """Move a complicated nested dictionary/list mixup into something simple.

    This is used to flatten the structure that is provided by a
    XML file into something more JSON like structure so that ElasticSearch
    is able to index it more efficently.
    """
    ret = {}
    if isinstance(data, dict):
        for key, value in data.iteritems():
            if isinstance(value, list):
                dubl = len(set(x.keys()[0] for x in value
                               if isinstance(x, dict))) == 1
                if dubl:
                    ret[key] = []
                    for item in value:
                        ret[key].append(simplify_dict(item))
                else:
                    ret[key] = {}
                    for item in value:
                        ret[key].update(simplify_dict(item))
            elif isinstance(value, dict):
                ret.update(simplify_dict(value))
            else:
                ret[key] = value
    else:
        for item in data:
            ret.update(simplify_dict(item))
    return ret


def to_dict(elem):
    """Moves a XML datastructure into a python dictionary that can be
    dumped to JSON.
    """
    # remove namespace
    tag = elem.tag.split('}', 1)[-1]
    data = None
    if elem.text and elem.text.strip():
        data = elem.text
    children = elem.getchildren()
    if children:
        data = map(to_dict, children)
    return simplify_dict({tag: data})
