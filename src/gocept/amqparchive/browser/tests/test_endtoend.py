# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.interfaces
import gocept.amqparchive.testing
import zope.component


class EndtoendTest(gocept.amqparchive.testing.SeleniumTestCase):

    def test_walking_skeleton(self):
        elasticsearch = zope.component.getUtility(
            gocept.amqparchive.interfaces.IElasticSearch)
        elasticsearch.index(dict(url='/foo', body='foo'), 'queue', 'message')
        s = self.selenium
        self.open('/')
        s.waitForElementPresent('css=li')
        s.assertText('css=li', '/foo')
