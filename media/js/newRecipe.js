function insertAdd(){
	var add = "<li class='box_mb'><canvas class='mb add'></canvas>"+
    "<p class='tag'>New</p></li>"
    $('#box_ingredient').find('ul').append(add);
}

function setTag(id, value){
	$.ajax({
        url:"update_label",
        type:"POST",
        async:true,
        dataType: "json",
        data: {"id":id,"value":value},
        beforeSubmit: function(){},
        success: function(data) {
        	showInfoPanel(htmlMsg12);
        	updateCurrentStep();
        },
        error: function(data){
        	showInfoPanel(htmlMsg20);
        }
	})
}

function insertIngredient(id, label, icon){
	var base = "<li class='box_mb' id="+id+">"+
      "<canvas class='mb stream' style='background:url(/media/"+icon+")')>" + "</canvas>"+
      "<p class='tag' contenteditable='true'>"+label+"</p></li>"
   	$('#box_ingredient').find('ul').append(base);
}

/***************************************
	ADDING NEW BUTTON
**************************************/

$(function(){ 

	$('.add').live('click',function() {
		var type = $(this).parents('.box').attr('id')
		var category;
		if( type == 'box_action'){
			type = gettext('Action')
			category = 'A';}
		else if( type == 'box_utensil'){
			type= gettext('Utensil')
			category = 'U';}
		else if( type == 'box_ingredient'){
			type= gettext('Ingredient')
			category = 'I'}
		// Updating the form header and category
		$('#mbForm h1').html(type.toUpperCase());
		$('#mbForm #category').val(category);
		$('#formMB #category').trigger('change');
		// CENTER DINAMIC SHIFT
		shiftBoxDinamic($('#mbForm'));
	});

	$('.minus').live('click',function() {
		$.ajax({
			url:"delete_last_step",
	        async:true,
	        data: {},
	        success: function(data) {
	        	if (data.state==true){
	        		updateUsedSteps();
	        		showInfoPanel(htmlMsg21);
	        	}
	        	else
	        		showInfoPanel(htmlMsg22);
	        }
		});
	});
});




/***************************************
	UPDATE LABEL
**************************************/

$(function(){
	$('.box_mb [contenteditable=true]').live('focusin',function(){
		$(this).data('value', {tag:$(this).html()} );
	}).live('focusout',function(){
		var pk = parseInt($(this).parent('.box_mb').attr('id'));
		var currentTag = $(this).html();
		if ( currentTag != $(this).data('value').tag)
			if (currentTag.length>2)
				setTag(pk,currentTag);
	});

	$('#box_step .stream,#box_action .stream,#box_utensil .stream,#box_ingredient .stream').live('click', function(){
		var id = $(this).parent('li').attr('id');
		addMBtoStep(id);
	});

	$('#cancelRecipe').click(function(){clearSession()});

  	$('#acceptRecipe').click(function(){
  	  $('#loadingPage').fadeIn();
  	  // console.log($('#loadingPage'));
      $.ajax({
        url:'upload_recipe',
        async:true,
        dataType: "json",
        success: function(data){
        	$('#loadingPage').fadeOut();
        	if (data.state == true){
	        	alert(htmlMsg23);
	        	$('#cancelRecipe').trigger('click');
	        	// window.location.href=window.location.href
	        }
	        else
	        	showInfoPanel(data.msg);	
        },
        error: function(){
        	$('#loadingPage').fadeOut();
        	showInfoPanel(htmlMsg24 );	
        }
      });
      
  	});
});


