$(function() {
	$('input.search-submit').css('display', 'none');
	$('.search-form label').click(function () {
		$(this).hide();
		$('#search-query').focus();
	});
	if (!$('#search-query').val())
		$('.search-form label').show();
	$('#search-query').focus(function () {
		$('.search-form label').hide();
	}).blur(function () {
		if (!$(this).val())
		  $('.search-form label').show()
	})
});

$(function() {
	$('.autocomplete').each(function(i, e) {
		e = $(e);
		var h = $('<input type="hidden">').attr('name', e.attr('name'));
		e.attr('name', e.attr('name') + '-label').after(h);
		e.autocomplete({
			source: function(request, callback) {
				$.get(e.data('data-search-url') || window.searchURL, {
					q: request.term + '*',
					format: 'autocomplete',
					"type": e.attr('data-type')
				}, callback, 'json');
			},
			minLength: 2,
			select: function(event, ui) {
				e.val(ui.item.label);
				h.val(ui.item.value);
				return false;
			}
		});
	});
});