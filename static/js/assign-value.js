
$(function(){
// window.onload = function(){	
	var article_csv = $('textarea#articlist').val();
	var ary_article = article_csv.split(',');

    var zodiac_signs = ["rat", "ox", "tiger", "hare", "dragon", "serpent", "horse", "sheep", "monky", "rooster", "dog", "boar"];
    for(var i = 0; i < zodiac_signs.length; i++){
    	$('.board').append('<textarea name="'+ zodiac_signs[i] +'" "cols="30" row="6"></textarea>');
    	// $('.board textarea[name="'+ zodiac_signs[i] +'"]').val(ary_article[i]);
    }
    $('.board').children('textarea').addClass('mdl-card');

	var dfd = new $.Deferred();
	setTimeout(function(){
    	$('.board textarea').css("display", "block");

		for(var j = 0; j < ary_article.length; j++){
			$('.board textarea[name="'+ zodiac_signs[j] +'"]').val(ary_article[j]);
		}
		dfd.resolve();
	}, 1000);
	return dfd.promise();
})
