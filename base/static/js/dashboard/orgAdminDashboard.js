$(document).ready(function handleModal(){
	$('.is-admin-toggle').change(function(){
		var toggleID = $(this).attr('id');
		var form = $('form#form-' + toggleID);
		var formData = form.serialize();
		var ajaxTargetUrl = form.attr('action');
		handleModalAjax(ajaxTargetUrl, 'POST', formData);
		successMessage('Updated organization admins');
	});
});