
$(function(){
	$('.my-up-button').on('click', function(){
		if(document.getElementById('alter-text') == ""){
			alert("ファイルを選択してください");
			return false;
		}
	})
})
