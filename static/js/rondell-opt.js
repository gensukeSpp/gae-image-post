
// window.onload = function(){
$(function(){
	$(document).on('rondell', function(){
		$("#rondell").rondell({
			size: {
				width: 480,
				height: 320
			},
			preset: "carousel",
			radius: {
				x: 200
			},
			center: {
				left: 240,
				top: 160
			},
			lightbox: {
				enabled: false,
    			displayReferencedImages: true
			},
			visibleItems: "6",
			itemProperties: {
				size: {
					width: 150,
					height: 100
				}
			},
			autoRoration: {
				enabled: true,
				direction: 0,
				once: false,
				delay: 5000
			}
		});
	})
	$.Deferred(function(dfd) {
	    setTimeout(function() {
	        //１秒まって 自分で resolve して次へ
		    if($(document).children('#container header #rondell').has('#detailink')){
		    	// alert('True');
		    	$(document).trigger('rondell');
		    }else{
		    	alert('False');
		    }
	        dfd.resolve();
	    }, 1000);
	})
});
// }
