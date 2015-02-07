/* editform */

(function($){
    $.bmf.editform = function(el, options){
        // To avoid scope issues, use 'base' instead of 'this'
        // to reference this class from internal events and functions.
        var base = this;

        // Access to jQuery and DOM versions of element
        base.$el = $(el);
        base.el = el;
      
        // Add a reverse reference to the DOM object
        base.$el.data("bmf.editform", base);

        base.init = function() {
            // load options
            base.options = $.extend({}, $.bmf.editform.defaultOptions, options);

            // initialization logic
            if (base.options.href == null) {
                // load target from the elements href attribute
                base.options.href = base.$el.attr('href');

            }
            base.$el.on('click', function (event) {
                event.preventDefault();
                base.open_formular();
            });
        }

        base.initialize_modal = function () {
            // initialize the modal
            $('#wrap').prepend('<div class="modal fade" id="bmfmodal_edit" tabindex="-1" role="dialog" aria-hidden="true"><div class="modal-dialog modal-lg"></div></div>');
            $('#bmfmodal_edit').modal({
                keyboard: true,
                show: false,
                backdrop: 'static'
            });

            // delete the modals content, if closed
            $('#bmfmodal_edit').on('hidden.bs.modal', function (e) {
                $('#bmfmodal_edit div.modal-dialog').empty();
            });

            //// reload the page if one save has appeared
            //$('#bmfmodal_edit').on('hide.bs.modal', function (e) {
            //    if ($('#bmfmodal_edit > div.page-reload').length == 1) {
            //        location.reload(false);
            //    }
            //});
        }

        base.open_formular = function () {
            // loads the formular data into the modal
            if ($('#bmfmodal_edit').length == 0) { base.initialize_modal() }

            dict = $.bmf.AJAX;
            dict.type = "GET";
            dict.url = base.options.href;
            $.ajax(dict).done(function( data, textStatus, jqXHR ) {

                if (data.success == true && data.reload == true) {
                    // reload page without refreshing the cache
                    location.reload(false);
                }

                $('#bmfmodal_edit div.modal-dialog').prepend(data.html);
                $('#bmfmodal_edit').modal('show');

                // manipulate form url
                // cause the template-tag which generates the form is not aware of the url
                var parent_object = $('#bmfmodal_edit div.modal-dialog div:first-child');
                var form_object = parent_object.find('form');
                // form_object.attr('action', base.options.href.split("?",1)[0]);
                form_object.attr('action', base.options.href);
                // apply bmf-form functions
                form_object.bmf_buildform();

                parent_object.find('button.bmfedit-cancel').click(function (event) {
                    // TODO check if there are multile forms and close modal or show next form
                    $('#bmfmodal_edit').modal('hide');
                });

                parent_object.find('button.bmfedit-submit').click(function (event) {
                    dict = $.bmf.AJAX;
                    dict.type = "POST";
                    dict.data = form_object.serialize();
                    dict.url = form_object.attr('action');
                    $.ajax(dict).done(function( data, textStatus, jqXHR ) {

                        //  # if an object is created or changed return the object's pk on success
                        //  'object_pk': 0, TODO
                        //  # on success set this to True
                        //  'success': False,
                        //  # reload page on success
                        //  'reload': False,
                        //  # OR redirect on success
                        //  'redirect': None,
                        //
                        //  # OR reload messages on success
                        //  'message': False, # TODO
                        //  # returned html
                        //  'html': None, # TODO
                        //  # return error messages
                        //  'errors': [], TODO

                        if (data.success == false) {
                            html = $($.parseHTML( data.html ));
                            form_object.html(html.find('form').html());
                            form_object.bmf_buildform();
                        }
                        else if (data.reload == true) {
                            // reload page without refreshing the cache
                            location.reload(false);
                        }
                        else if (data.redirect != null) {
                            window.location.href=data.redirect;
                        }
                        else {
                            $('#bmfmodal_edit').modal('hide');
                        }
                    });
                });
            });
        }
      
        // Run initializer
        base.init();
    };

    // default options
    $.bmf.editform.defaultOptions = {
        href: null,
        debug: false
    };

    // register as jquery function
    $.fn.bmf_editform = function(options){
        return this.each(function(){
            (new $.bmf.editform(this, options));
        });
    };
})(jQuery);
$(document).ready(function() {
    $('.bmf-edit').bmf_editform();
    $('.btn-bmfdelete').bmf_editform();
    $('.btn-bmfupdate').bmf_editform();
    $('.btn-bmfclone').bmf_editform();
    $('.btn-bmfworkflow').bmf_editform();
});
