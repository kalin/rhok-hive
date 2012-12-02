jQuery(document).ready(function($) {

	$.ajaxSetup({
		type: 'POST'
	});

	var $pin = $('#pin-input');
	var pinMaxLength = 5;

	// Keyboard Key
	$('.keyboard .key').addClass('btn-large').removeClass('btn-primary');


	$('.keyboard .key').on('click', function(e) {
		e.preventDefault();
		$pin.focus();
		if($pin.val().length < pinMaxLength) {
			$pin.val($pin.val() + $(this).text());
			$('#pin-input').keyup();
		}
	});

	// Clear PIN
	$('#pin-clear').on('click', function(e) {
		e.preventDefault();
		$pin.val('');
		$('#response').html('');
	});

	// Check when PIN is complete
	$('#pin-input').on('keyup', function(e) {
		if($pin.val().length == pinMaxLength) {
			$.ajax({
				url: '/beelogger/check-user-pin/',
				data: {
					pin: $pin.val(),
					csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
				},
				success: function(response) {
					$('#response').html(response);
				}
			});
		}
		if($pin.val().length < pinMaxLength) {
			$('#response').html('');
		}
	});


});
