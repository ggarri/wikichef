

function updateRecipes(){
	function addRecipe(id, title, desc, listI, path){
		var base = "<li class='recipe' id='"+id+"'>"+
            "<section class='header'>"+
            "<p>"+title+"</p>"+
            "<canvas class='imgRecipe' style='background:url(/media/"+path+")'></canvas>"+
            "</section>"+
            "<section class='list_I'>"+
            "<label> List Ingredients: </label>"+
            "</section>"+
            "<section class='desc'>"+
            "<label> Decription: </label>"+
            "<p>"+desc+"</p>"+
            "</section></li>"
        $('#listRecipes ul').append(base);
        recipe = $('#listRecipes ul li:last')
        for (var i=0 ; i<listI.length; i++){
        	I = listI[i]
        	var ingredient = '<p>' + I.label +' ('+I.amount+' '+I.unit+') </p>'
        	$(recipe).find('.list_I label').after(ingredient)
        }
	}

	$.ajax({
		url:'get_brief_recipes',
        async:true,
        type:'GET',
        dataType: "json",
        data: {'level': $('#levelSimilarity .slider_text').val()/100.0 },
        success: function(data){
        	if (data.state==true){
               $('#loadingPage').fadeIn();
                $('#listRecipes ul').empty()
                if (data.msg.length == 0)
                    addRecipe(-1, 'None', 'There are not any with this ingredients', new Array(), 'imgs/defaultRecipe.png');
                else {
            		for (var i=0; i<data.msg.length; i++){
            			var recipe = data.msg[i]
            			addRecipe(recipe.id, recipe.title, recipe.desc, recipe.LI, recipe.path);
            		}
                }
        		updateBoxFloat($('#listRecipes .box_float'));
                $('#loadingPage').fadeOut();
        	}
        	else 
        		showInfoPanel('Error while loading Recipes');
     	}
	});
}


function updateIngredientsSelected(){
    function addIngredientSelected(id,label,icon){
        var base = "<li class='box_mb' id="+id+">"+
        "<canvas class='mb stream' style='background:url(/media/"+icon+")'> </canvas>"+
        "<p class='tag'>"+label+"</p></li>";
        $('#box_ingredient_selected ul').append(base);
    }

    $.ajax({
        url:'get_ingredients_selected',
        async:true,
        dataType: "json",
        data: {},
        success: function(data){
            if (data.state == true){
                $('#box_ingredient_selected ul').empty();
                for (var i=0 ; i<data.msg.length; i++){
                    var I = data.msg[i];
                    addIngredientSelected(I.id,I.label,I.icon);
                }
            }
            else
                showInfoPanel('Error while loading the ingredients selected');
        }
    })

}

function fillRecipeForm(recipe){
    console.debug(recipe);
    $('.overPanel .title h1').html(recipe.title);
    $('.overPanel .title canvas').css('background','url(/media/'+recipe.img+')');
    $('.overPanel .ingredients ul').empty()
    for (var i=0 ; i<recipe.LI.length; i++){
        var I = recipe.LI[i]
        var base='<li>'+I.label+' ('+I.amount+' '+I.unit+') </li>';
        $('.overPanel .ingredients ul').append(base);
    }
    $('.overPanel .description p').html(recipe.desc);
    $('.overPanel .duration p').html(recipe.time + ' min');
    $('.overPanel .difficulty p').html(recipe.difficulty);
    $('.overPanel .steps ul').empty()
    for (var i=0 ; i<recipe.steps.length; i++){
        var step = recipe.steps[i]
        var base='<li><label>(Step '+(i+1)+')'+step.label+'</label>'+
        '<p> Comment :'+step.comments+'</p><p>Amounts: </p></li>';
        $('.overPanel .steps ul').append(base);
        for (var j=0 ; j<step.LI.length; j++){
            var I = step.LI[j];
            var subase = I.label + ' (' + I.amount + ' '+ I.unit+')';
            $('.overPanel .steps ul li:last p:last').append(subase+', ');
        }
    }
    
}

$(function(){

    $('#box_ingredient canvas').live('click',function(){
        id = $(this).parent('.box_mb').attr('id');
        var exists = false
        for (var i=0 ; i<$('#box_ingredient_selected .box_mb').length; i++)
            if ( $('#box_ingredient_selected .box_mb').eq(i).attr('id') == id)
                exists = true
        if (exists == false) {
            $.ajax({
                url:'add_ingredient',
                async:true,
                type:'GET',
                dataType: "json",
                data: {'id':id},
                success: function(data){
                    if (data.state == false)
                        showInfoPanel('Error while adding the ingredient.')
                    else{
                        updateIngredientsSelected();
                        updateRecipes();
                    }
                }
            });
        }
        else
            showInfoPanel('Element was already added')
    });

    $('#box_ingredient_selected canvas').live('click',function(){
        id = $(this).parent('.box_mb').attr('id');
        $.ajax({
            url:'del_ingredient',
            async:true,
            dataType: "json",
            data: {'id':id},
            success: function(data){
                if (data.state == false)
                    showInfoPanel('Error while adding the ingredient.')
                else{
                    updateIngredientsSelected();
                    updateRecipes();
                }
            }
        });
    });


    $('#levelSimilarity .slider').live('mouseup',function(){
        updateRecipes();
        $(this).trigger('focusout');
    });

    $('.overPanel').css({
       'height': $('#content').css('height'),
       'width': $('#content').css('width'),
       'top': $('#page_header').css('height'),
       'left': $('#content').css('width')/2,
    });

    $('#acceptDetails').click(function(){
        $('.overPanel').effect('blind',null,700);
    });

    $('.recipe').live('click',function(){
       id = $(this).attr('id');
        $.ajax({
            url:'get_recipe',
                async:true,
                type:'GET',
                dataType: "json",
                data: {'id':id},
                success: function(data){
                    if (data.state == true){
                        $('#loadingPage').fadeIn();
                        fillRecipeForm(data.msg);
                        $('#loadingPage').fadeOut();
                        $('.overPanel').fadeIn('slow'); 
                    }
                    else
                        showInfoPanel('Error while loading recipe datas');
                }
        })
    });

    $('.overPanel').hide(); // Firstly hidden
    addSlider('levelSimilarity',0,100,80);
	updateRecipes();
    updateIngredientsSelected();
});