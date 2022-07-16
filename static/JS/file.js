setInterval(function() {
            $.getJSON('/update_storages', function(result)
            {
                if (result.answer == 'True')
                {
                    window.location.reload()
                }
            }).fail(function() {

            });
    }, 5000);