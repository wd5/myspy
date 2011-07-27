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
    });