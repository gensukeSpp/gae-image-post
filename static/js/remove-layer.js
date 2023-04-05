
$(function(){
	var $under_layer = $('.graylayer');
	var $upper_layer = $('.overlayer');
	var href = location.href;

	var dfd = new $.Deferred();
	
	var firststep = function(){
		setTimeout(function(){
			$under_layer.fadeIn("slow");
			dfd.resolve();
		}, 700);
		return dfd.promise();
	}

	var secondstep = function(){
		setTimeout(function(){
			$upper_layer.fadeIn().css({"top": "25%",
									"bottom": "25%"});	
			dfd.resolve();
		}, 700);
		// return dfd.promise();
	}

	$('#delete').on('click', function(){
		firststep().then(function(){
			return secondstep();
		}).then(function(){
			var rpl_url = href.replace('edit', 'delete');
			$upper_layer.children('form#confirm-delete').attr("action", rpl_url);		
		})
	});
})
