var useAnalyticsCookieOptions = {
	expires: 365,
	path: '/',
	secure: 'https:' == document.location.protocol,
};
var rejectableCookies = ['__utma', '__utmb', '__utmc', '__utmz'];
var analyticsInjected = false;

$(function () {
	var analyticsControls = $('#analytics-controls').addClass('analytics-controls');

	analyticsControls.children().remove();
	if (doNotTrack)
		analyticsControls.append($(
			'<p>Your browser is currently sending the <a href="http://en.wikipedia.org/wiki/Do_Not_Track">Do ' +
			'Not Track</a> header, and so Analytics is disabled.</p>'));
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
					.append($('<span class="analytics-notice-dismiss" title="Accept and dismiss"></span>'))
					
				)
				);
	}
	if ($.cookie('use_analytics') != 'false')
		injectAnalytics();
});

function analyticsControl(enabled) {
	$.cookie('use_analytics', enabled ? 'true' : 'false', useAnalyticsCookieOptions);
	if (enabled)
		injectAnalytics();
	else
		for (var i in rejectableCookies)
			$.cookie(rejectableCookies[i], null, {domain: '.' + window.location.hostname, path: '/'});
	$('#analytics-notice').slideUp('fast', function() { $('#analytics-notice').remove(); });
	return false;
}

var _gaq = _gaq || [];

function injectAnalytics() {
	if (!analyticsInjected) {
		analyticsInjected = true;

	_gaq.push(['_setAccount', analyticsID]);
	_gaq.push(['_trackPageview']);

	var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
}
}
