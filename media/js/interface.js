function addSlider(box,min,max,value){
	box = '#' + box;
	$(box).children(".slider" ).slider({
	  range: "min",
	  min: min,
	  max: max,
	  value: value,
	  slide: function( event, ui ) {
	    $(box).children('.slider_text').val( ui.value);
	  }
	});
	$(box).children(".slider_text" ).val( value );
	$('.slider_text').live('select',function(){
		$(this).parent().children('.slider').slider('value',int($(this).val()) );
	});
}

function shiftBoxDinamic(box){
	// console.log('entra',$('#box_dinamic').children(':visible'),$(box))
	if ( $('#box_dinamic').children(':visible') != $(box)){
		$('#box_dinamic').data('last',$('#box_dinamic').children(':visible'));
		$('#box_dinamic').children(':visible').hide();
		// SHOWING OR HIDING UNITS
		// console.log($('#box_dinamic').children(box));
		$(box).show();
	}
}

function showInfoPanel(msg){
	$('#infoPanel').children('p').html(msg);
	$('#infoPanel').fadeIn('normal',function(){
		setTimeout("$('#infoPanel').hide('show')",2500);
	})
}

function setState(state){
	$.ajax({
		url: 'set_state',
        type:"GET",
        async:true,
        dataType: "json",
        data: {'state':state},
        success: function(){ console.log('state changed');}
    });
}

function clearSession(reload){
	$.ajax({
	    url:'clear_session',
	    async:true,
	    dataType: "json",
	    success: function(){
	    	showInfoPanel('Session deleted');
	    	console.log(reload)
	    	window.location.href=window.location.href
	    },
	    error: function(){
	    	showInfoPanel(gettext('Deleting session had a error') );	
    	}
	});	
}

function updateAutocomplete(input, list) {
	$( input ).autocomplete({
		source: list
	});
}


/***************************************
	BROWSER INGREDIENTS
**************************************/

$(function(){
	$('#browserIngredient').data('value',{'last':''});

	$('#browserIngredient').keyup(function(){
		if( $(this).data('value').last != $(this).attr('value') ){
			$(this).data('value').last = $(this).attr('value');
			// console.log('changing');
			$.ajax({
				url:"/recipes/instant_searching_ingredient",
		        type:"POST",
		        async:true,
		        dataType: "json",
		        data: {"pattern":$(this).attr('value')},
		        beforeSubmit: function(){},
		        success: function(data) {
		        	var ingredients = new Array();
		        	var i;
		        	$('#box_ingredient').find('ul').html('');
		        	for (i=0; i<data.length;i++){
		        		insertIngredient(data[i].id, data[i].label, data[i].icon )
		        		ingredients[i] = data[i].label
		        	}
		        	insertAdd();
		        	updateAutocomplete($('#browserIngredient'), ingredients )
		        	// updateBoxFloat($('#box_ingredient .box_float'))
		        }
			});
		}
		
		
	});
});


$(function(){
	
	$(window).scroll(function(){
    	$('#infoPanel').css("top", $(window).scrollTop());
	});

	$(window).mousemove(function(e){
	      window.mouseXPos = e.pageX;
	      window.mouseYPos = e.pageY;
   	}); 

   	$('#loadingPage').hide();

	$('[contenteditable=true]').hover( function(){
		$(this).addClass('editable');
	}, function(){
		$(this).stop().removeClass('editable');
	});


	$('.box_mb').live('hover',function(ev){
		if (ev.type == 'mouseenter') {
            $(this).find('.tag').animate({
				'font-weight' : 'bold'
			},'fast');
			$(this).find('aside').animate({
				'opacity' : 0.8
			},'slow');
        }
        else{
            $(this).find('.tag').stop().animate({
				'font-weight' : 'normal'
			},'fast');
			$(this).find('aside').stop().animate({
				'opacity' : 0
			},'fast');
    	}
	});

	/**** BUTTON MENU *****/
	$('.buttonMenu').click(function(){
		$('.buttonMenu').removeClass('buttonMenu2');
		$(this).addClass('buttonMenu2');
	});

	$('.box').hover(function(){
		$(this).addClass('box_hover');
		$(this).children('.box_header').addClass('box_header_hover');
	},function(){
		$(this).removeClass('box_hover');
		$(this).children('.box_header').removeClass('box_header_hover');
	});

	$('.mb').live('click', function(){
		$(this).parent().stop().effect('explode',{},700).fadeIn();
	});

});





