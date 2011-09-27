
function updateCurrentStep(){
	function showCurrentStep(msg){
		$('#currentStep').html(msg[0]);
	}
	function updateFormCurrentStep(data){
		$('#formCorrectStep fieldset')
		var custom = $('#formCorrectStep fieldset p:first')
		$('#formCorrectStep fieldset').empty();
		$('#formCorrectStep fieldset').append(custom);
		for (var i=0 ; i<data.length; i++){
			obj = document.createElement('input');
			$(obj).attr('type','radio');
		    $(obj).attr('value',i);
		    $(obj).attr('id','selectCorrectStep');
		    $(obj).attr('name','selectCorrectStep');
		    // console.log($(obj));
		    $('#formCorrectStep fieldset').append('<p></p>')
		    $('#formCorrectStep fieldset p:last').append(obj);
		    $('#formCorrectStep fieldset p:last').append(data[i]);
		}
	}
	$('#loadingPage').fadeIn();
	$.ajax({
		url:'get_current_step',
		async:true,
		dataType: 'json',
		success: function(data){
			// console.debug(data);
			if (data.state == true){
				// console.debug(data)
				if (data.msg.length == 1){
					showCurrentStep(data.msg);
					$('#currentStep').data('isOK',0);
				}
				else if(data.msg.length == 0){
					$('#currentStep').html(htmlMsg14);
					$('#currentStep').data('isOK',-1);
				}
				else{
					updateFormCurrentStep(data.msg);
					shiftBoxDinamic('#correctStepForm');
					$('#currentStep').data('isOK',-1);
				}
			}
			else{
				$('#currentStep').html(htmlMsg15);
				$('#currentStep').data('isOK',-1);
			}
		},
		error: function(){
			showInfoPanel(htmlMsg16)
		}
	});
	$('#loadingPage').fadeOut();
}

function updateBallContainer(){
	function addButtonSelected(id,label,icon){
		var base = "<li class='box_mb' id="+id+">"+
		"<canvas class='mb stream' style='background:url(/media/"+icon+")')></canvas>"+
        "<aside>"+label+"</aside></li>";
		$('#ballContainer ul').append(base);
	}

	$.ajax({
		url:'get_selected_buttons',
		async:true,
		dataType: "json",
		success: function(data){
		  $('#ballContainer ul').html('');
		  if (data.state == true){
		    var id,style;
		    for (var i=0; i<data.msg.length; i++){
		      id = data.msg[i].id;
		      label = data.msg[i].label
		      icon = data.msg[i].icon
		      // style = $('#'+id).children('canvas').attr('style');
		      // label = $('#'+id).children('p').html()
		      addButtonSelected(id,label,icon);
		    }
		    containerBallResize();
		  }
		}
	});
}

function updateUsedSteps(){
	function addStepUsed(id, label, tag, icon){
		var base = "<li class='box_mb' id="+id+" style='display :inline-block;'>"+
        "<canvas class='mb stream' style='background:url(/media/"+icon+")'> </canvas>"+
        "<p class='tag'>"+tag+"</p>"+
        "<aside>"+label+"</aside></li>";
		$('#box_step .minus').parent('.box_mb').before(base);
		// $('#box_step .stream:last').css('background-image','url(/media/'+icon+')');
	}
	$.ajax({
		url:'get_used_steps',
		async:true,
		dataType: "json",
		success: function(data){
			$('#box_step .stream').parent('li').remove();
			if (data.state == true){
				for (var i=0 ; i<data.msg.length ; i++){
					step = data.msg[i]
					addStepUsed(step.id,step.label,step.tag,step.icon)
				}
				updateCurrentStep();
				updateBallContainer();
				updateBoxFloat($('#box_step .box_float'))
			}
		}
	});	
}


function containerBallResize(){
    var pos_left = $('#ball').offset().left;
    var pos_top = $('#ball').offset().top;
    var w = $('#ball').width()-10;
    $("#ballContainer").css(
      {'top':pos_top+10,'left':pos_left+10,
      'width':w-20,'height':w-20,'border-radius':Math.round(w/2)}
    );
}

function addMBtoStep(id){
	$('#loadingPage').fadeIn();
	$.ajax({
		url:'add_mb_to_step',
		type:'GET',
		async:true,
		dataType:'json',
		data:{'id':id},
		success: function(data){ 
			$('#loadingPage').fadeOut();
			if(data.state == true){
				updateCurrentStep();
				updateBallContainer();
				showInfoPanel(htmlMsg17);
			}
			else{
				showInfoPanel(data.msg);
			}
		},
		error: function(data){
			$('#loadingPage').fadeOut();
		}
	});
}

function delMBtoStep(id){
	$('#loadingPage').fadeIn();
	$.ajax({
		url:'del_mb_to_step',
		type:'GET',
		asyn:false,
		datatype:'json',
		data:{'id':id},
		success: function(data){
			$('#loadingPage').fadeOut();
			if (data.state == true){
				updateCurrentStep();
				updateBallContainer();
				showInfoPanel(htmlMsg18);
			}
			else{
				showInfoPanel(data.msg);
			}
		}
	});
}

function setSentenceStep(sentence){
	$('#loadingPage').fadeIn();
	// console.log(sentence)
	$.ajax({
		url:'set_current_step',
		async:true,
		dataType: 'json',
		type:'GET',
		data:{'sentence':sentence},
		success: function(data){
			$('#loadingPage').fadeOut();
			if (data.state == true)
				showInfoPanel(htmlMsg11);
			else
				showInfoPanel(data.msg);
		},
		error: function(){
			$('#loadingPage').fadeOut();
			showInfoPanel(htmlMsg13);
		}
	});
}


/***************************************
	USING MAGIC BUTTONS
**************************************/


$(function() {


	$('#ballContainer .stream').live('click',function(){
		var id = $(this).parent('li').attr('id');
		delMBtoStep(id);
	});


	/**** INFORMATION BALL *****/
	$('.box_ball').hover(function(){
		$('#ball').removeClass('ballNormal');
		$('#ball').addClass('ballHover');
		$('#ball').stop()
		setTimeout(containerBallResize,500);
	},function(){
		$('#ball').removeClass('ballHover');
		$('#ball').addClass('ballNormal');
		$('#ball').stop()
		setTimeout(containerBallResize,500); 
	});

	$('#ballButton').hover(function(){
    	$('#ballButton').stop().effect('bounce',{},300);
	},function(){
		$('#ballButton').stop()
	});

	$('#ballButton').click(function(){
		if ($('#currentStep').data('isOK') == -1)
			showInfoPanel(htmlMsg19)
		else{
			$('#formStep .step').html($('#currentStep').html().toUpperCase())
			updateIngredientSection()
			shiftBoxDinamic('#stepForm');
		}
	});


	$('#currentStep').focusin(function(){
		$(this).data('value', {sentence:$(this).html()} );
	}).focusout(function(){
		var currentSentence = $(this).html();
		if ( currentSentence != $(this).data('value').sentence)
			setSentenceStep(currentSentence);
	});

	containerBallResize();
	updateCurrentStep();
	updateBallContainer();
	updateUsedSteps();
});

