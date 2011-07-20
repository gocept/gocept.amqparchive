# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.interfaces
import gocept.amqparchive.testing
import zope.component


class EndtoendTest(gocept.amqparchive.testing.SeleniumTestCase):

    def test_enter_search_term_returns_urls_of_results(self):
        elasticsearch = zope.component.getUtility(
            gocept.amqparchive.interfaces.IElasticSearch)
        elasticsearch.index(
            dict(url='foo/bar/baz.xml', body='foo'), 'queue', 'message')
        s = self.selenium
        self.open('/')
        s.type('id=query', 'foo')
        s.click('id=search')
        s.waitForElementPresent('css=li')
        s.assertText('css=li', '/messages/foo/bar/baz.xml')
