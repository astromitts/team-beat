function handleModalAjax(ajaxTargetUrl, method, formData) {
	var postData;
	$.ajax({
		method: method,
		url: ajaxTargetUrl,
		dataType: 'json',
		data: formData,
		async: false,
		success: function(data) {
			postData = data;
		},
		error: function () {
			postData = {}
			postData.status = 'error';
			postData.error_message = 'Unable to complete request: unkown error';
		}
	});
	return postData;
}

function handleChangeLeadOnTeam(userId, ajaxTargetUrl) {
	var formData = {'user_id': userId, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()}
	var postData = handleModalAjax(ajaxTargetUrl, 'POST', formData);
	var targetRow = $('tr#teamlead-row');
	targetRow.html(postData.htmlResult);
}

function handelRemoveTeamMemberModal(sourceButton, modalId) {
	var teamMemberId = sourceButton.attr('data-teammember-id');
	var teamMemberName = sourceButton.attr('data-display-name');
	var nameSpan = $('span#teammember-name');
	var ajaxTargetUrl = sourceButton.attr('data-ajax-target');
	var formData = $('form#remove-teammember-' + teamMemberId).serialize();
	nameSpan.html(teamMemberName);
	$('#' + modalId).modal('show');

	$('#js-remove-teammember').click(function executeRemoveTeamMember(){
		postData = handleModalAjax(ajaxTargetUrl, 'POST', formData);
		if (postData.status == 'success') {
			$('tr#teammember_' + teamMemberId).remove();
		}
		$('#' + modalId).modal('hide');
	});
}

function handelRemoveTeamAdminModal(sourceButton, modalId) {
	var teamAdminId = sourceButton.attr('data-teamadmin-id');
	var teamMemberName = sourceButton.attr('data-display-name');
	var nameSpan = $('span#teammember-name');
	var ajaxTargetUrl = sourceButton.attr('data-ajax-target');
	nameSpan.html(teamMemberName);
	$('#' + modalId).modal('show');

	$('#js-remove-teammember').click(function executeRemoveTeamMember(){
		var formData = $('form#remove-teamadmin-' + teamAdminId).serialize();
		postData = handleModalAjax(ajaxTargetUrl, 'POST', formData);
		if (postData.status == 'success') {
			$('tr#teamadmin-row-' + teamAdminId).remove();
		}
		$('#' + modalId).modal('hide');
	});
}

function handleAddAdminToTeam(userId, ajaxTargetUrl) {
	var formData = {'user_id': userId, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()}
	var postData = handleModalAjax(ajaxTargetUrl, 'POST', formData);
	var targetTable = $('table#teamadmin-rows tbody');
	targetTable.prepend(postData.htmlResult);
	bindShowModal($('button#removeadmin-' + postData.teamAdminId));
}

function handleAddUserToTeam(userId, ajaxTargetUrl) {
	var formData = {'user_id': userId, 'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()}
	var postData = handleModalAjax(ajaxTargetUrl, 'POST', formData);
	var targetTable = $('table#teammember-rows tbody');
	targetTable.prepend(postData.htmlResult);
	bindShowModal($('button#remove-teammember-' + postData.teamMemberId));
}

function clearUserSearch() {
	var resultTable = $('table#search-results');
	resultTable.html('');
	$('input#id_email_address').val('');

}

function handleUserSearchModal(sourceButton, modalId) {
	clearUserSearch();
	$('#' + modalId).modal('show');
	var searchApiURL = sourceButton.attr('data-ajax-target');
	var resultHandlerFunction = sourceButton.attr('data-result-target-handler');
	var resultHanlerUrl = sourceButton.attr('data-result-target-url');
	var resultTable = $('table#search-results');
	$('form#modal-user-search').submit(function executeUserSearch(event){
		event.preventDefault();
		resultTable.css('display', 'none');
		resultTable.html('');
		var formData = $(this).serialize();
		var searchResults = handleModalAjax(searchApiURL, 'GET', formData);
		if (searchResults) {
			searchResults.searchResult.forEach(function displayResult(user){
				var rowHTML = '<tr><td>' + user.displayName + ' (' + user.email + ') </td><td><button class="btn btn-success js-handle-result" data-user-id="'+user.id+'">add</button></td></tr>';
				resultTable.append(rowHTML);
			});
			resultTable.css('display', '');
			$('button.js-handle-result').click(function(){
				var userId = $(this).attr('data-user-id');
				window[resultHandlerFunction](userId, resultHanlerUrl);
				clearUserSearch();
				$('#' + modalId).modal('hide');
			});
		}
	});
}

function bindShowModal(element) {
	element.click(function showModal(){
		var handler = $(this).attr('data-js-handler');
		var modalId = $(this).attr('data-modal-id');
		window[handler]($(this), modalId);
	});
}

$(document).ready(function handleModal(){
	bindShowModal($('.js-modal-trigger'));
});