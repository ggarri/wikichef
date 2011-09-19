/**************************************
  BOX STYLE - FLOAT LISTS
**************************************/

function moveFloatBox(box){
	var first = $(box).data('index').first;
	var last = $(box).data('index').last;
	var n = $(box).data('list').n;
	var pos = parseInt(first / $(box).data('list').showed);
	var i;
	$(box).find('li').hide();
	for(i=first ; i<last && i<=n; i++){
		$(box).find('li').eq(i).fadeIn();
	}
	if( $(box).data('list').extra == true){
		$(box).find('.add').parent('li').fadeIn();
		$(box).find('.minus').parent('li').fadeIn();
	}

	if( first == 0)
		$(box).find('.arrow').eq(1).removeClass('arrowBefore').addClass('arrowBefore2');
	else
		$(box).find('.arrow').eq(1).removeClass('arrowBefore2').addClass('arrowBefore');
	if(last > n-1)
		$(box).find('.arrow').eq(0).removeClass('arrowNext').addClass('arrowNext2');
	else
		$(box).find('.arrow').eq(0).removeClass('arrowNext2').addClass('arrowNext');

	// console.log(first,last);
	$(box).find('.markerBall').animate({'opacity':'0.4'});
	$(box).find('.markerBall').eq(pos).animate({'opacity':'1'});
}


function updateMarkers(box){
	var box_markers = $(box).find('.marker');
	var i = $(box).data('list').n / $(box).data('list').showed;
	if ( i-parseInt(i) > 0.0 || i==0){ i = parseInt(++i);}
	$(box_markers).empty();
	// console.log($(box),$(box_markers),i)
	for (i ; i>0; i--){
		$(box_markers).append('<canvas class="markerBall"></canvas>');
	}
	$(box_markers).hide();
}


function updateBoxFloat(box) {
	var fils= parseInt($(box).outerHeight(true)/$(box).find('li').outerHeight(true));
	var cols= parseInt($(box).outerWidth(true)/$(box).find('li').outerWidth(true));
	var showed = fils*cols;
	var length = $(box).find('li').length
	var extra = false
	if( $(box).find('.add').length != 0 || $(box).find('.minus').length != 0){
		extra = true;
		showed--;
		length--;
	}
	$(box).data('list', 
		{ n: length, showed:showed, extra: extra}
	);
	var list = $(box).data('list');
	$(box).data('index', { first:0, last:list.showed});
	// console.log(list,$(box).data('index'));
	updateMarkers(box);
	moveFloatBox(box);
}


$(function(){


	/**** ARROWS and MARKER*****/
	$('.box_float').each(function(){
		$(this).append('<aside class="arrow"></aside><aside class="arrow"></aside>');
		$(this).append('<aside class="marker"></aside>');
		updateBoxFloat($(this));
	});

	$('.marker').each( function(){
		var box_float = $(this).parent('.box_float');
		var top = $(box_float).offset().top;
		var left = $(box_float).offset().left;
		var width = $(box_float).width();
		var height = $(box_float).height();
		$(this).css({'top': top+height,'left': left+(width/2)-($(this).width()/2)});
	});
		

	$('.arrow').each( function(e){
		var top = $(this).parent().offset().top;
		var left = $(this).parent().offset().left;
		var height = $(this).parent().height();
		// Define the parameter to raise list elements.
		if (e%2 == 0){
			$(this).addClass('arrowNext');
			left += $(this).parent().width();
			$(this).click(function(){
				box_float = $(this).parent('.box_float');
				index = box_float.data('index');
				list = box_float.data('list');
				// console.log(list,index);
				if(index.last+1 <= list.n){
					index.first = index.last;
					index.last += list.showed;
					if ( index.last > list.n){
					 	index.last = list.n; 
					}
				}
				// updateBoxFloat(box_float);
				moveFloatBox(box_float);
				$(this).toggle().delay(400).toggle();
			});
		}
		else{
			$(this).addClass('arrowBefore');
			left -= $(this).width();
			$(this).click(function(){
				box_float = $(this).parent('.box_float');
				index = box_float.data('index');
				list = box_float.data('list');

				if(index.first > 0){
					index.last = index.first;
					index.first -= list.showed;
					if ( index.first < 0){ index.first = 0; }
				}
				// updateBoxFloat(box_float);
				moveFloatBox(box_float);
				$(this).toggle().delay(400).toggle();
			});
		}
		$(this).css({'top': top,'left': left, 'height':height });
		$(this).hide();
	});


	$('.box_float').hover(function(){
		$(this).find('.arrow').fadeIn();
		$(this).find('.marker').fadeIn();
		},function(){
		$(this).find('.arrow').hide();
		$(this).find('.marker').hide();
	});

});
