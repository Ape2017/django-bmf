/*!
django BMF
*/

(function($){
    if(!$.bmf){
        $.bmf = new Object();
    };

    // Keys
    $.bmf.KEYS = {
        ESC: 27,
        TAB: 9,
        RETURN: 13,
        UP: 38,
        DOWN: 40
    };

    $.bmf.AJAX = {
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        },
        crossDomain: false,
        dataType: 'json',
        error: function(jqXHRm, textStatus, errorThrown) {
            console.log( errorThrown+" ("+textStatus+")" );
        },
        statusCode: {
            403: function(jqXHRm, textStatus, errorThrown) {
                alert( gettext("Error 403\n You don't have permission to view this page") );
            },
            404: function(jqXHRm, textStatus, errorThrown) {
                alert( gettext("Error 404\n Page not found") );
            },
            405: function(jqXHRm, textStatus, errorThrown) {
                alert( gettext("Error 405\n Method not allowed") );
            },
            500: function(jqXHRm, textStatus, errorThrown) {
                if (jqXHRm.responseText == undefined) {
                    alert( gettext("Error 500\n An Error occured while rendering the page") );
                }
                else {
                    alert( jqXHRm.responseText );
                }
            }
        }
    };
})(jQuery);

$.extend($.fn.treegrid.defaults, {
    expanderExpandedClass: 'glyphicon glyphicon-minus',
    expanderCollapsedClass: 'glyphicon glyphicon-plus'
});
