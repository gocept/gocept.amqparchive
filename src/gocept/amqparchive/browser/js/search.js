// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt

// require('jquery')
// require('jsclass')
// require('json-template')
// require('elasticsearch')
// require('template')


(function($) {
gocept = window.gocept || {};
gocept.amqparchive = gocept.amqparchive || {};


gocept.amqparchive.ElasticSearch = Class.extend({

    __init__: function(url, index, type) {
        var self = this;
        self.elasticsearch = new ElasticSearch({url: url});
        self.index = index;
        self.type = type;
    },

    search: function(query, callback) {
        var self = this;
        self.elasticsearch.search({
            indices: self.index,
            types: self.type,
            queryDSL: {query: {'text': {'_all': query}}},
            callback: function(json, xhr) {
                if (xhr.status == 200) {
                    callback(json);
                } else {
                    var response = $.parseJSON(xhr.responseText);
                    gocept.amqparchive.display_error(response['error']);
                }
            }
        });
    }

});


gocept.amqparchive.ES = new gocept.amqparchive.ElasticSearch(
    '/elasticsearch', 'queue', 'message');


var RESULT_TEMPLATE = new gocept.amqparchive.Template(
    '{.repeated section @}<li><a href="/messages/{_source.path}">'
    + '/messages/{_source.path}</a></li>{.end}'
);


gocept.amqparchive.run_search = function() {
    gocept.amqparchive.ES.search($('#query').val(), function(data) {
        $('#count').html('total hits: ' + data.hits.total);
        $('#results').html(RESULT_TEMPLATE.expand(data.hits.hits));
    });
};


var RETURN = 13;

$(window).bind('load', function() {
    $('#search').bind('click', gocept.amqparchive.run_search);
    $('#query').bind('keydown', function(event) {
        if (event.keyCode == RETURN) {
            gocept.amqparchive.run_search();
        }
    });

    $('#query').focus();
});

})(jQuery);