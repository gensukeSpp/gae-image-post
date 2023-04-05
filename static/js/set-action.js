
$(function(){

	var href = location.href;
	
	$('#edit .inside-edit form#article-form').attr("action", href);
	// var rpl_hrf = href.replace('edit', 'delete');
	// $('#edit .inside-edit form#delete-form').attr("action", rpl_hrf);
})
