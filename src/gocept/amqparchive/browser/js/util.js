// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt

// require('jsontemplate')


(function($) {
gocept = window.gocept || {};
gocept.amqparchive = gocept.amqparchive || {};

gocept.amqparchive.create_template = function(contents) {
    return jsontemplate.Template(contents, {
        default_formatter: 'html'
    });
};

})(jQuery);