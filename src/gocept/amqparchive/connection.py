# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.interfaces
import gocept.amqprun.interfaces
import pyes
import zope.component
import zope.interface


class ElasticSearch(pyes.ES):

    zope.interface.implements(gocept.amqparchive.interfaces.IElasticSearch)

    def __init__(self):
        settings = zope.component.getUtility(
            gocept.amqprun.interfaces.ISettings)
        return super(ElasticSearch, self).__init__(
            settings['gocept.amqparchive.elastic_hostname'])

    def index_immediately(self, *args, **kw):
        """ElasticSearch by default doesn't update itself immediately,
        so a newly indexed document is searchable only after a short delay.
        This method helps avoiding littering the tests with time.sleep(1)
        """
        kw.setdefault('querystring_args', {})['refresh'] = True
        return super(ElasticSearch, self).index(*args, **kw)
