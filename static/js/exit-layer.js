
$(function(){
	$(document).on('click', '.graylayer', function(){
		$('.overlayer').fadeOut();
		$('.overlayer img').remove();
		$('.graylayer').fadeOut();
	});
})
	