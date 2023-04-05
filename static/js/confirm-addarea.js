
$(function(){
	var article_csv = $('textarea#articlist').val();
	var ary_article = article_csv.split(',');

	for(var j = 0; j < ary_article.length; j++){
		$('.board').append('<p class="cat' + (j + 1) + '"></p>');
		$('.board p.cat' + (j + 1)).text(ary_article[j]);
	}

})
