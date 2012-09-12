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

