function teamCard() {

}

function placeTeamCards(teams) {
	var teamRow = document.getElementById('myteams');
	teams.forEach(function placeTeamCard(team){
		var teamContainer = document.createElement('div');
		teamContainer.setAttribute('class', 'col');

		var teamCard = document.createElement('div');
		teamCard.setAttribute('class', 'teamcard');

		var teamTitle = document.createElement('div');
		teamTitle.setAttribute('class', 'teamcard_title');
		teamTitle.innerHTML = team.teamName;

		teamCard.append(teamTitle);

		var statusContainer = document.createElement('div');
		statusContainer.setAttribute('class', 'teamcard_status');
		
		var statusDiv = document.createElement('div');
		statusDiv.setAttribute('class', 'teamcard_status-statusstring');
		
		var statusLink = document.createElement('a');
		var statusButton = document.createElement('button');
		if ( team.status != null ) {
			statusDiv.append(document.createTextNode('Your status is ' + team.status));
			statusButton.innerHTML = 'Change Status';
		} else {
			statusDiv.append(document.createTextNode(
				'You need to set your status for today'));
			statusButton.innerHTML = 'Set Status';
		}
		
		statusLink.append(statusButton);
		statusDiv.append(statusLink);

		teamCard.append(statusDiv);
		teamContainer.append(teamCard);
		teamRow.append(teamCard);
	});
}

function loadDashboard() {
	var refreshUrl = $('input#js-refresh-url').val();
	$.ajax({
		method: 'GET',
		url: refreshUrl,
		dataType: 'json',
		success: function loadDashboardData(dashboardData) {
			placeTeamCards(dashboardData.teams);
		}
	});
}


$(document).ready(function dashboard(){
	var autoRefresh = false;
	//loadDashboard();
	if (autoRefresh) {
		var dashLoop = window.setInterval(function startDashLoop(){
			refreshDashboard();

		}, 5000);
	}
});