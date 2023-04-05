
$(function(){
	$target = $('.board').children('textarea');

	var dfd = new $.Deferred();
	setTimeout(function(){
		$('.board .loader').fadeOut(1500);
		$target.addClass('mdl-card').fadeIn(2500)
		dfd.resolve();
	}, 400);
	return dfd.promise();
})
