# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.interfaces
import gocept.amqparchive.testing


class SearchTest(gocept.amqparchive.testing.SeleniumTestCase):

    def setUp(self):
        super(SearchTest, self).setUp()
        self.open('/')
        self.eval("""\
window.gocept.amqparchive.ES.search = function(query, callback) {
    callback({hits: {hits: [{_source: {url: 'foo/bar/baz.xml'}}]}});
};
""")

    def test_enter_key_starts_search(self):
        s = self.selenium
        s.type('id=query', 'foo')
        s.keyDown('id=query', r'\13')
        s.waitForElementPresent('css=li')
        s.assertText('css=li', '/messages/foo/bar/baz.xml')
