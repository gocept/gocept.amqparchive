# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.interfaces
import gocept.amqparchive.testing


class EndtoendTest(gocept.amqparchive.testing.SeleniumTestCase):

    layer = gocept.amqparchive.testing.ENDTOEND_LAYER

    def test_enter_search_term_returns_urls_of_results(self):
        self.elastic.index(
            dict(path='foo/bar/baz.xml', body='foo'), 'queue', 'message')
        s = self.selenium
        self.open('/search/')
        s.type('id=query', 'foo')
        s.click('id=search')
        s.waitForElementPresent('css=li')
        s.assertText('css=li', '/messages/foo/bar/baz.xml')
