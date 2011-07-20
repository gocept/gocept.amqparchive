// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt

// require('jquery')
// require('jsclass')
// require('json-template')
// require('elasticsearch')


(function($) {
gocept = window.gocept || {};
gocept.amqparchive = gocept.amqparchive || {};


gocept.amqparchive.ElasticSearch = Class.extend({

    __init__: function(url) {
        var self = this;
        self.elasticsearch = new ElasticSearch({url: url});
    },

    search: function(query, callback) {
        var self = this;
        self.elasticsearch.search({
            indices: 'queue',
            types: 'message',
            queryDSL: {query: {'text': {'_all': query}}},
            callback: function(json, xhr) {
                // XXX error handling
                callback(json);
            }
        });
    }

});


gocept.amqparchive.ES = new gocept.amqparchive.ElasticSearch('/elasticsearch');


gocept.amqparchive.create_template = function(contents) {
    return jsontemplate.Template(contents, {
        default_formatter: 'html'
    });
};


var RESULT_TEMPLATE = gocept.amqparchive.create_template(
    '{.repeated section @}<li><a href="/messages/{_source.url}">'
    + '/messages/{_source.url}</a></li>{.end}'
);


gocept.amqparchive.run_search = function() {
    gocept.amqparchive.ES.search($('#query').val(), function(data) {
        $('#results').html(RESULT_TEMPLATE.expand(data.hits.hits));
    });
};


$(window).bind('load', function() {
    $('#search').bind('click', gocept.amqparchive.run_search);
    // XXX also bind #query keydown "return"
});

})(jQuery);