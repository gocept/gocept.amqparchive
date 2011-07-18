# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.interfaces
import gocept.amqprun.interfaces
import pyes
import zope.component
import zope.interface


class ElasticSearch(pyes.ES):

    zope.interface.implements(gocept.amqparchive.interfaces.IElasticSearch)

    @property
    def settings(self):
        return zope.component.getUtility(gocept.amqprun.interfaces.ISettings)

    def __init__(self):
        # socket doesn't accept unicode for hostname/port
        return super(ElasticSearch, self).__init__(
            self.settings['gocept.amqparchive.elastic_hostname'].encode(
                'utf8'))

    def index(self, *args, **kw):
        """ElasticSearch by default doesn't update itself immediately,
        so a newly indexed document is searchable only after a short delay.
        For tests we want to force an immediate refresh.

        Note: the autorefresh-parameter in pyes is not sufficient for this
        purpose, as it only applies to search(), but not to get(), for example.
        """
        if self.settings.get('gocept.amqparchive.elastic_autorefresh', False):
            kw.setdefault('querystring_args', {})['refresh'] = True
        return super(ElasticSearch, self).index(*args, **kw)
