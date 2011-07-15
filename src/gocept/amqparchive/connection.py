# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.interfaces
import gocept.amqprun.interfaces
import pyes
import zope.component
import zope.interface


@zope.interface.implementer(gocept.amqparchive.interfaces.IElasticSearch)
def ElasticSearch():
    settings = zope.component.getUtility(gocept.amqprun.interfaces.ISettings)
    return pyes.ES(settings['gocept.amqparchive.elastic_hostname'])
