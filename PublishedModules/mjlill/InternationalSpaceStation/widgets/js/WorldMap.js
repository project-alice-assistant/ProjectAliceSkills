(function () {
    function positionISS() {
        $.ajax({
            datatype: 'json',
            url: 'http://api.open-notify.org/iss-now.json',
            success: function (data) {
                let latitude = data['iss_position']['latitude'];
                let longitude = data['iss_position']['longitude'];

                let x = (longitude + 180) * ($('.WorldMap_map').width() / 360);

                let siny = Math.sin(latitude * Math.PI / 180);
                siny = Math.min(Math.max(siny, -0.9999), 0.9999);
                let y = $('.WorldMap_map').height() * (Math.log((1 + siny) / (1 - siny)) / (4 * Math.PI));


                $('.WorldMap_satellite').css('top', y - 10);
                $('.WorldMap_satellite').css('left', x - 15);
            }
        });

        setTimeout(function () {
            positionISS()
        }, 5000);
    }
    positionISS();
})();