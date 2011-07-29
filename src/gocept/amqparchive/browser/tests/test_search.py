# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.amqparchive.interfaces
import gocept.amqparchive.testing


class SearchTest(gocept.amqparchive.testing.SeleniumTestCase):

    def setUp(self):
        super(SearchTest, self).setUp()
        self.open('/search/')

    def test_enter_key_starts_search(self):
        self.eval("""\
window.gocept.amqparchive.ES.search = function(query, callback) {
    callback({hits: {
        total: 7,
        hits: [{_source: {path: 'foo/bar/baz.xml'}}]}});
};
""")

        s = self.selenium
        s.type('id=query', 'foo')
        s.keyDown('id=query', r'\13')
        s.waitForElementPresent('css=li')
        s.assertText('css=li', '/messages/foo/bar/baz.xml')

    def test_shows_total_hit_count(self):
        self.eval("""\
window.gocept.amqparchive.ES.search = function(query, callback) {
    callback({hits: {
        total: 7,
        hits: [{_source: {path: 'foo/bar/baz.xml'}}]}});
};
""")

        s = self.selenium
        s.type('id=query', 'foo')
        s.keyDown('id=query', r'\13')
        s.waitForElementPresent('css=li')
        s.assertText('css=li', '/messages/foo/bar/baz.xml')
        s.assertText('id=count', '*7*')

    def test_elasticsearch_error_is_displayed(self):
        self.eval("""\
window.gocept.amqparchive.ES.elasticsearch.search = function(params) {
    params.callback({}, {
        status: 404,
        responseText: '{"error": "provoked error"}'
    });
};
""")

        s = self.selenium
        s.keyDown('id=query', r'\13')
        s.waitForElementPresent('id=error-dialog')
        s.assertText('id=error-dialog', '*provoked error*')
