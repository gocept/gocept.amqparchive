# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.xml
import gocept.amqprun.interfaces
import logging
import zope.component


log = logging.getLogger(__name__)


@zope.component.adapter(gocept.amqprun.interfaces.IMessageStored)
def index_message(event):
    message = event.message
    data = dict(
        path=event.path,
        data=gocept.amqparchive.xml.jsonify(message.body),
    )
    data.update(message.header.__dict__)

    elastic = zope.component.getUtility(
        gocept.amqparchive.interfaces.IElasticSearch)
    try:
        elastic.index(data, 'queue', 'message')
    except:
        log.warning('Error connecting to ES', exc_info=True)
