(function () {
	let APIKEY = '';
	let UNITS = '';
	let LOCATION = '';
	let UNITS_NAME = '';

	function refresh() {
		let $icon = '';
		$.get('http://api.openweathermap.org/data/2.5/weather?q=' + LOCATION + '&appid=' + APIKEY + '&units=' + UNITS_NAME).done(function(answer) {
			$('#CurrentWeather > #temperature').html(answer['main']['temp'] + '°' + UNITS);
			$('#CurrentWeather > #location').attr('title', LOCATION);
			$('#myWeatherIcon').remove();
			$icon = $('<img src="http://openweathermap.org/img/wn/' + answer['weather'][0]['icon'] + '.png" alt="icon" id="myWeatherIcon">');
		}).fail(function() {
			$icon = $('<i class="fas fa-exclamation-triangle weather-fetch-failed" aria-hidden="true"></i>');
		}).always(function() {
			$('#weatherIcon').append($icon);
		});
	}

	$.ajax({
		url: '/home/widget/',
		data: JSON.stringify({
			skill: 'OpenWeatherMap',
			widget: 'CurrentWeather',
			func: 'baseData',
			param: ''
		}),
		contentType: 'application/json',
		dataType: 'json',
		type: 'POST'
	}).done(function(answer) {
		APIKEY = answer['apiKey'];
		UNITS = answer['units'];
		LOCATION = answer['location'];
		UNITS_NAME = answer['unitsName'];

		$('#CurrentWeather > #location').html(LOCATION);
	}).then(function() {
		refresh();
		setInterval(function() {refresh()}, 5 * 60 * 1000);
	});
})();
