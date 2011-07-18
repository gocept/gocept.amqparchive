# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqprun.interfaces
import zope.component


@zope.component.adapter(gocept.amqprun.interfaces.IMessageStored)
def index_message(event):
    message = event.message
    data = dict(
        path=event.path,
        body=message.body,
        )
    data.update(message.header.__dict__)

    elastic = zope.component.getUtility(
        gocept.amqparchive.interfaces.IElasticSearch)
    elastic.index(data, 'queue', 'message')
