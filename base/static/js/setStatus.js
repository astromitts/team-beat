function bindSetStatus(){
	$('.status_select-card').click(function selectStatus(){
		$('div#submit-form').css('display', 'none');
		$('.status-border-selected').removeClass('status-border-selected');
		$(this).addClass('status-border-selected');
		var formField = $('input#selected-status');
		formField.val($(this).attr('data-selected-status'));
		$('button#confirm-status').removeAttr('disabled');
	});
}

function bindConfirmStatus() {
	$('button#confirm-status').click(function revealSubmitForm(){
		$('#submit-form').css('display', '');
		var currentStatus = $('input#selected-status').val();
		if( currentStatus == 'red' || currentStatus == 'yellow') {
			$('#red-yellow-required').css('display', '');
			$('#status-additional-info-lead').prop('required', true);
		} else {
			$('#red-yellow-required').css('display', 'none');
			$('#status-additional-info-lead').removeAttr('required');
		}
	});
}

$(document).ready(function setStatus(){
	bindSetStatus();
	bindConfirmStatus();
});