(function () {
    function positionISS() {
        $.ajax({
            datatype: 'json',
            url: 'http://api.open-notify.org/iss-now.json',
            success: function (data) {
                let latitude = parseFloat(data['iss_position']['latitude']);
                let longitude = parseFloat(data['iss_position']['longitude']);
                
                let x = $('.WorldMap_map').width()  / 360 * ( longitude + 180 );
                let y = $('.WorldMap_map').height() / 180 * ( -latitude + 90 ) ;

                $('.WorldMap_satellite').css('top', y - 10);
                $('.WorldMap_satellite').css('left', x - 15);
                $('.WorldMap_satellite').show();
            }
        });

        setTimeout(function () {
            positionISS()
        }, 5000);
    }
    positionISS();
})();
