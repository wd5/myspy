$(document).ready( function() {
$("a[href='#select_all']").click( function() {
$("#" + $(this).attr('rel') + " input:checkbox:enabled").attr('checked', true);
return false;
});

$("a[href='#select_none']").click( function() {
	$("#" + $(this).attr('rel') + " input:checkbox:enabled").attr('checked', false);
		return false;

	});
});

