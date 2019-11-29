var filter_by = null;
$().ready(function() {
    $('table').tablesort();
    $('.ui.dropdown').dropdown('set selected', filter_by);

    $('.message .close')
        .on('click', function () {
            $(this)
                .closest('.message')
                .transition('fade')
            ;
        })
    ;
});

