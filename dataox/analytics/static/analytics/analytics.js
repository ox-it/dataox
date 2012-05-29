var useAnalyticsCookieOptions = {
	expires: 365,
	path: '/',
	secure: 'https:' == document.location.protocol,
};
var rejectableCookies = ['__utma', '__utmb', '__utmc', '__utmz'];
var analyticsInjected = false;

$(function () {
	$.ajaxSetup({
		  cache: true
	});

	$.getScript(staticURL + "jquery-cookie/jquery.cookie.js", function() {

	var analyticsControls = $('#analytics-controls').addClass('analytics-controls')
	analyticsControls.children().remove();
	if (doNotTrack)
		analyticsControls.append($(
			'<p>Your browser is currently sending the <a href="http://en.wikipedia.org/wiki/Do_Not_Track">Do' +
			'Not Track</a> header, and so Analytics is disabled.'));
	else {
		analyticsControls.append($('<p>Enable or disable Google Analytics:</p>'));
		var options = $('<ul/>')
			.append($('<li><input type="radio" id="analytics-enable" name="analytics-option" value="true"/><label for="analytics-enable">Enabled</lable></li>'))
			.append($('<li><input type="radio" id="analytics-disable" name="analytics-option" value="false"/><label for="analytics-disable">Disabled</lable></li>'));
		options.find('input').click(function() { analyticsControl($(this).val() == "true")}).each(function (i, e) {
			if ($(e).val() == $.cookie('use_analytics'))
				$(e).attr("checked", true);
		});
		analyticsControls.append(options);
		
	}
	
	if (doNotTrack)
		return;

	if ($.cookie('use_analytics') == undefined) {
		$('body').prepend(
			$('<div id="analytics-notice">This site uses cookies to track usage with the aim of improving your experience. If you prefer not to receive such cookies, you may </div>')
				.append(
					$('<a id="analytics-reject" href="#">disable them</a>').click(function() { return analyticsControl(false); }))
				.append('. See our ')
				.append(
					$('<a>privacy policy</a>').attr('href', privacyPolicyURL))
				.append(' for more information, and to change your preference later. ')
				.append(
					$('<a id="analytics-accept" href="#">Accept and dismiss</a>').click(function() { return analyticsControl(true); })
					.append($('<img class="analytics-notice-dismiss" alt="">').attr('src', staticURL + 'analytics/dismiss.png'))
					
				)
				);
	}
	if ($.cookie('use_analytics') != 'false')
		injectAnalytics();
	});
});

function analyticsControl(enabled) {
	$.cookie('use_analytics', enabled ? 'true' : 'false', useAnalyticsCookieOptions);
	if (enabled)
		injectAnalytics();
	else
		for (var i in rejectableCookies)
			$.cookie(rejectableCookies[i], null);
	$('#analytics-notice').slideUp();
	return false;
}

function injectAnalytics() {
	if (!analyticsInjected) {
		analyticsInjected = true;
		var _gaq = _gaq || [];
		_gaq.push(['_setAccount', 'UA-32168758-1']);
		_gaq.push(['_trackPageview']);

		var src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
		$.getScript(src);
	}
}
