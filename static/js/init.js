$(document).ready( function() {
	$(".maincheckbox1").click( function() {
		if( $('.maincheckbox1').hasClass('ui-state-active')) {
			// $('.group1').attr('checked', false);
			$('.group1').removeAttr("checked");
			$('.group1').next().removeClass('ui-state-active');
		} else {
			$('.group1').attr('checked', true);
			$('.group1').next().addClass('ui-state-active');
		} 
	}); 	
	$(".send_form1").click( function() {  		
			$('.group1').attr('checked', true);
			$('.group1').next().addClass('ui-state-active');
			$('.maincheckbox1').addClass('active');
			$('#hd1').next().addClass('ui-state-active'); 
			$('#filter').submit(); 
		 
	});  
	
	$(".maincheckbox2").click( function() {
		if( $('.maincheckbox2').hasClass('ui-state-active')) {
			// $('.group2').attr('checked', false);
			$('.group2').removeAttr("checked");
			$('.group2').next().removeClass('ui-state-active');
		} else {
			$('.group2').attr('checked', true);
			$('.group2').next().addClass('ui-state-active');
		} 
	}); 	
	$(".send_form2").click( function() {  		
			$('.group2').attr('checked', true);
			$('.group2').next().addClass('ui-state-active');
			$('.maincheckbox2').addClass('active');
			$('#hd2').next().addClass('ui-state-active'); 
			$('#filter').submit(); 
		 
	});
	
	$(".maincheckbox3").click( function() {
		if( $('.maincheckbox3').hasClass('ui-state-active')) {
			// $('.group3').attr('checked', false);
			$('.group3').removeAttr("checked");
			$('.group3').next().removeClass('ui-state-active');
		} else {
			$('.group3').attr('checked', true);
			$('.group3').next().addClass('ui-state-active');
		} 
	}); 	
	$(".send_form3").click( function() {  		
			$('.group3').attr('checked', true);
			$('.group3').next().addClass('ui-state-active');
			$('.maincheckbox3').addClass('active');
			$('#hd3').next().addClass('ui-state-active'); 
			$('#filter').submit(); 
		 
	}); 
	
});




/*$(document).ready( function() {
	$(".maincheckbox1").click( function() { alert('ok');
		if( $('.maincheckbox1').hasClass('active')) {
			$('.group1').removeAttr("checked");
			$('.group1').next().removeClass('ui-state-active'); 
			$('.maincheckbox1').removeClass('active'); 
			$('#hd1').next().removeClass('ui-state-active');
		} else {
			$('.group1').attr('checked', true);
			$('.group1').next().addClass('ui-state-active');
			$('.maincheckbox1').addClass('active');
			$('#hd1').next().addClass('ui-state-active');
		}  
	});   
	
	$(".send_form").click( function() {
			$('#filter').submit();  
		}); 
		
	$(".maincheckbox2").click( function() {
		if( $('.maincheckbox2').hasClass('active')) {
			$('.group2').removeAttr("checked");
			$('.group2').next().removeClass('ui-state-active'); 
			$('.maincheckbox2').removeClass('active'); 
			$('#hd2').next().removeClass('ui-state-active');
		} else {
			$('.group2').attr('checked', true);
			$('.group2').next().addClass('ui-state-active');
			$('.maincheckbox2').addClass('active');
			$('#hd2').next().addClass('ui-state-active');
		}        
		$('#filter').submit();
	}); 
	
	$(".maincheckbox3").click( function() {
		if( $('.maincheckbox3').hasClass('active')) {
			$('.group3').removeAttr("checked");
			$('.group3').next().removeClass('ui-state-active'); 
			$('.maincheckbox3').removeClass('active'); 
			$('#hd3').next().removeClass('ui-state-active');
		} else {
			$('.group3').attr('checked', true);
			$('.group3').next().addClass('ui-state-active');
			$('.maincheckbox3').addClass('active');
			$('#hd3').next().addClass('ui-state-active');
		}    
		$('#filter').submit();
	}); 	
	
	
});


*/

/*
$(document).ready( function() {
	$(".maincheckbox1").click( function() {
		if( $('#maincheckbox1').hasClass('ui-state-active')) {
			// $('.group1').attr('checked', false);
			$('.group1').removeAttr("checked");
			$('.group1').next().removeClass('ui-state-active');
		} else {
			$('.group1').attr('checked', true);
			$('.group1').next().addClass('ui-state-active');
		}
	});
	
	$(".maincheckbox2").click( function() {
		if( $('.maincheckbox2').hasClass('ui-state-active')) {
			// $('.group2').attr('checked', false);
			$('.group2').removeAttr("checked");
			$('.group2').next().removeClass('ui-state-active');
		} else {
			$('.group2').attr('checked', true);
			$('.group2').next().addClass('ui-state-active');
		}
return false;
	});
	
	$(".maincheckbox3").click( function() {
		if( $('.maincheckbox3').hasClass('ui-state-active')) {
			// $('.group3').attr('checked', false);
			$('.group3').removeAttr("checked");
			$('.group3').next().removeClass('ui-state-active');
		} else {
			$('.group3').attr('checked', true);
			$('.group3').next().addClass('ui-state-active');
		}
return false;
	});
});
*/