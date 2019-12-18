(function () {
	$.ajax({
		datatype: 'json',
		url: 'http://api.open-notify.org/astros.json',
		success: function (data) {
			$.each(data['people'], function (key, val) {
				$('#WhosAboard_astronaut_list').append('<li class="WhosAboard_astonaut_list_item"><span class="fa-li"><i class="fas fa-user-astronaut"></i></span>' + val['name'] + '</li>');
			});
		}
	})
})();