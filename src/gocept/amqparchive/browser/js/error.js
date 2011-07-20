// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt

// require('jquery')
// require('jquery-ui')
// require('template')


(function($) {
gocept = window.gocept || {};
gocept.amqparchive = gocept.amqparchive || {};


var DIALOG_TEMPLATE = new gocept.amqparchive.Template(
    '<div id="error-dialog">'
    + '<p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>An error occured:</p>'
    + '<p>{message}</p>'
    + '</div>');


gocept.amqparchive.display_error = function(text) {
    $('body').append(DIALOG_TEMPLATE.expand({message: text}));
    $('#error-dialog').dialog({
        modal: true,
        title: 'Error',
        buttons: {'Close': function() {
            $(this).dialog('close');
            $(this).dialog('destroy');
            $(this).remove();
        }}
    });
};

})(jQuery);