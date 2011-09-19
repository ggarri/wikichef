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
        	showInfoPanel('That button was changed correctly.\n Thanks for you colaboration. ');
        	updateCurrentStep();
        },
        error: function(data){
        	showInfoPanel('That button could not be changed correctly.Try it again later. \nThanks for you colaboration. ');
        }
	})
}

/***************************************
	ADDING NEW BUTTON
**************************************/

$(function(){ 

	$('.add').live('click',function() {
		var type = $(this).parents('.box').attr('id')
		var category;
		if( type == 'box_action'){
			type = 'Action'
			category = 'A';}
		else if( type == 'box_utensil'){
			type='Utensil'
			category = 'U';}
		else if( type == 'box_ingredient'){
			type='Ingredient'
			category = 'I'}
		// Updating the form header and category
		$('#mbForm h1').html('NEW - '+type.toUpperCase());
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
	        		showInfoPanel('Step deleted correctly');
	        	}
	        	else
	        		showInfoPanel('It was imposible to delete the last Step');
	        }
		});
	});
});




/***************************************
	UPDATE LABEL
**************************************/

$(function(){
	$('.box_mb [contenteditable=true]').focusin(function(){
		$(this).data('value', {tag:$(this).html()} );
	}).focusout(function(){
		var pk = parseInt($(this).parent('.box_mb').attr('id'));
		var currentTag = $(this).html();
		if ( currentTag != $(this).data('value').tag)
			if (currentTag.length>2)
				setTag(pk,currentTag);
	});

	$('#cancelRecipe').click(function(){clearSession()});

  	$('#acceptRecipe').click(function(){
      $.ajax({
        url:'upload_recipe',
        async:true,
        dataType: "json",
        success: function(data){
        	if (data.state == true){
	        	alert('Recipe saved correctly.');
	        	$('#cancelRecipe').trigger('click');
	        	// window.location.href=window.location.href
	        }
	        else
	        	showInfoPanel(data.msg);	
        },
        error: function(){
        	showInfoPanel('It is imposible without steps.');	
        }
      });
  	});
});

