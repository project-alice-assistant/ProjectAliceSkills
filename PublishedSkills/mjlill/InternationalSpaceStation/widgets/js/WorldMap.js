(function () {
	let counter = 5;

	function positionISS() {
		$.ajax({
			datatype: 'json',
			url: 'http://api.open-notify.org/iss-now.json',
			success: function (data) {
				let latitude = parseFloat(data['iss_position']['latitude']);
				let longitude = parseFloat(data['iss_position']['longitude']);

				let x = $('.WorldMap_map').width() / 360 * (longitude + 180);
				let y = $('.WorldMap_map').height() / 180 * (-latitude + 90);

				$('.WorldMap_satellite').css('top', y - 12);
				$('.WorldMap_satellite').css('left', x - 12);
				$('.WorldMap_satellite').show();

				counter += 1;
				if (counter >= 5) {
					let $marker = $('<div class="WorldMap_dots">&#8226;</div>');
					$marker.css('top', y - 9);
					$marker.css('left', x - 3);
					$('.WorldMap_map').append($marker);
					if ($('.WorldMap_map').children('.WorldMap_dots').length > 1000) {
						$('.WorldMap_map').find(':nth-child(2)').remove();
					}
					counter = 0;
				}
			}
		});

		setTimeout(function () {
			positionISS()
		}, 5000);
	}

	positionISS();
})();
