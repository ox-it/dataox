$(function() {
	return;
	var moreText = "show more sub-categories";
	var fewerText = "show fewer sub-categories";
	$('body.equipment-browse li.equipment-category').each(function(i, e) {
		var li = $(this);
		li.find('li').slice(5).css('display', 'none');
		if (li.find('li').length > 5) {
			li.find('ul').after($('<a href="#"/>').text(moreText).click(function() {
				var toggle = $(this);
				if (toggle.text() == moreText)
					toggle.text(fewerText).prev('ul').find('li').slideDown();
				else
					toggle.text(moreText).prev('ul').find('li').slideUp();
				return false;
			}));
		}
	});
});

$(function() {
  $('.facet h3').not('.facet-active h3').collapsible();
  $('.facet-active h3').collapsible(false);
});

$(function() {
	$('.autocomplete').each(function(i, e) {
		var defaultParams = {format: 'autocomplete'};
		for (var i = 0; i < e.attributes.length; i++) {
			var attribute = e.attributes[i];
			if (attribute.name.slice(0, 18) == 'data-autocomplete-')
				defaultParams[attribute.name.slice(18)] = attribute.value;
		}

		e = $(e);
		var searchURL = e.attr('data-search-url') || window.searchURL;
		var h = $('<input type="hidden">').attr('name', e.attr('name')).val(e.val());
		e.attr('name', e.attr('name') + '-label').after(h);

		if (e.val()) {
			var originalVal = e.val();
			e.val("looking up…");
			$.get(searchURL, $.extend({}, defaultParams, {
				q: 'uri:"'+originalVal+'"'
			}), function(data) {
				e.val(data ? data[0].label : originalVal);
			});
		}
		e.autocomplete({
			source: function(request, callback) {
				$.get(searchURL, $.extend({}, defaultParams, {
					q: request.term + '*'
				}), callback, 'json');
			},
			minLength: 2,
			focus: function(event, ui) {
				e.val(ui.item.label);
				return false;
			},
			select: function(event, ui) {
				e.val(ui.item.label);
				h.val(ui.item.value);
				return false;
			}
		});
	});
});