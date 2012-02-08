// DROP DOWN BY PAGELINES


$(document).ready(function () {
	
	$("ul.dropdown > li").hover(function(){
        $(this).addClass("menuhover");
        $(this).find('#header_sprite').fadeIn(0);
    }, function(){	
        $(this).removeClass("menuhover");
        $(this).find('#header_sprite').fadeOut(0);

    });

});