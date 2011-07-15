# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface


class IElasticSearch(zope.interface.Interface):
    """A connection to an ElasticSearch server (pyes.ES object).

    The pyes documentation at <http://packages.python.org/pyes/>
    is helpful, while a little outdated in details (e.g. parameter names).
    When in doubt, use the source, Luke.
    """
