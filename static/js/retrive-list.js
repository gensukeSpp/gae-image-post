
$(window).on('load', function(){
	var dfd = new $.Deferred();
	var myImagesLayer = 
		// event.preventDefault();
		$.ajax({
			type: 'GET',
			/* 読み込むHTMLページのURL */
			url: '../../inner',
			dataType: 'html',
			success: dfd.resolve,
			error: dfd.reject
		// }).then(
		// 	function(data){$('#list').append(data);},
		// 	function(xhr, textStatus, errorThrown){cosole.log('Error! ' + textStatus + ' ' + errorThrown);
		})
	// });

	var mateContentsLayer = 
		// event.preventDefault();
		// var dfd = new $.Deferred();
		$.ajax({
			type: 'GET',
			/* 読み込むHTMLページのURL */
			url: '../../mate',
			dataType: 'html',
			success: dfd.resolve,
			error: dfd.reject
		// }).then(
		// 	function(data){$('#top').append(data);},
		// 	function(xhr, textStatus, errorThrown){cosole.log('Error! ' + textStatus + ' ' + errorThrown);
		})
	// });

	$.when(myImagesLayer, mateContentsLayer).done(function(data1, data2){
		$('#list').append(data1);
        // $('#list').children().addClass('my-image');
		$('#rondell').append(data2);
	})
})
