$(document).ready(function(){

	var els = document.getElementsByTagName('img');
	for (var i = 0; i < els.length; i++){
		if (els[i].className === 'wpsc_buy_button'){
			var id = 'wpsc_buy_button'+i;
			els[i].id = id;
			fn_cart_AddEvent(els[i],'click',fn_cart_clickBtnBuy,id);
		}
	}
	
	for (var i = 1; i <= 2; i++){
		$('#cart_box_'+i).click(function(){
			$.fancybox.showActivity();
			$.ajax({type:"GET", url:'/cart/', data:'', success: function(data){ fn_cart_showData(data); }});
			return false;
		});
	}
});
function fn_cart_clickBtnBuy(id){
	$.fancybox.showActivity();
	$.ajax({type:"POST", url:window.location, data:fn_cart_sendData(document.getElementById(id).parentNode), success: function(data){ fn_cart_showData(data); }});
}
function fn_cart_AddEvent(obj, type, fn, id)
{
	if (obj == null){ return; }
	if (arguments.length == 3){
		if (obj.addEventListener) {obj.addEventListener(type, fn, true);}
		else { if (obj.attachEvent) { obj.attachEvent( "on"+type, fn ); } } 
	}
	if (arguments.length == 4){
		if (obj.addEventListener) {obj.addEventListener(type, function(){fn(id);}, true);}
		else { if (obj.attachEvent) { obj.attachEvent( "on"+type, function(){fn(id);} ); } } 
	}
}
function fn_cart_click(_this,search_form){

	$('body,html').animate({scrollTop: 0}, 100);
	
	var frm;
	if (search_form){
		frm = fn_searchParentFrom(_this);
	} else {
		frm = _this.parentNode;
	}
	
	$.fancybox.showActivity();
	$.ajax({type:"POST", url:'/cart/', data:fn_cart_sendData(frm), success: function(data){ fn_cart_showData(data); }});

	return false;
}
function fn_cart_showData(data){
	
	function f(data){
		var p = data.indexOf('[[*'); if (p == -1){ return data; }
		var p2 = data.indexOf('*]]'); if (p2 == -1){ return data; }
		var count = data.slice(p+3,p2);
		var el = document.getElementById('the_box_count');
		if (el != null){ el.innerHTML = count; }
		return data.slice(p2+3);
	}
	$.fancybox(f(data));
}
function fn_cart_sendData(frm){

	if (frm == null){ return ''; }
	
	var sendData = '';
	
	var inps = new Array('input','textarea');

	for (var j = 0; j < inps.length; j++){
	
		var frm_inps = frm.getElementsByTagName(inps[j]);
		
		for (var i = 0; i < frm_inps.length; i++){
			var name = frm_inps[i].name;
			if (name !== ''){
				sendData += ((sendData==='')?'':'&')+name+'='+frm_inps[i].value.replace(/&/g,'%26');
			}
		}
	}
	return sendData;
}
function fn_searchParentFrom(el){
	while (el.tagName.toLowerCase() !== 'body'){
		if (el.tagName.toLowerCase() === 'form'){
			return el;
		}
		el = el.parentNode;
		if (el == null){ break; }
	}
	return null;
}