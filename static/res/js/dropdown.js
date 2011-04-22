// DROP DOWN BY PAGELINES

var $j = jQuery.noConflict();

$j(document).ready(function () {
	
	$j("ul.dropdown > li").hover(function(){
        $j(this).addClass("menuhover");
        $j(this).find('#header_sprite').fadeIn(0);
    }, function(){	
        $j(this).removeClass("menuhover");
        $j(this).find('#header_sprite').fadeOut(0);

    });

});