(function () {
	let APIKEY = '';
	let UNITS = '';
	let LOCATION = '';
	let UNITS_NAME = '';

	function refresh() {
		$.get('http://api.openweathermap.org/data/2.5/weather?q=' + LOCATION + '&appid=' + APIKEY + '&units=' + UNITS_NAME).done(function(answer) {
			console.log(answer);
			$('#CurrentWeather > #temperature').html(answer['main']['temp'] + '°' + UNITS);

			let $icon = $('<img src="http://openweathermap.org/img/wn/' + answer['weather'][0]['icon'] + '.png" alt="icon" id="myWeatherIcon">');
			$('#weatherIcon').remove($('#myWeatherIcon'));
			$('#weatherIcon').append($icon);
		})
	}

	$.ajax({
		url: '/home/widget/',
		data: JSON.stringify({
			module: 'OpenWeatherMap',
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
