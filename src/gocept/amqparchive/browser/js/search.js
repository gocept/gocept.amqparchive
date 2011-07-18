(function($) {

var elasticsearch = new ElasticSearch({port: 9212});

$(window).bind('load', function() {
    elasticsearch.search({
        queryDSL: {query: {'text': {'_all': 'foo'}}},
        indices: 'queue',
        types: 'message',
        callback: function(json, xhr) {
            $.each(json.hits.hits, function(i, hit) {
                $('#results').append($('<li>' + hit._source.url + '</li>'));
            });
        }
    });
});

})(jQuery);