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
	var sendData = fn_cart_sendData(document.getElementById(id).parentNode);
	$.ajax({type:"POST", url:window.location, data:sendData, success: function(data){ fn_cart_showData(data); }});
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
	fn_cart_tel_valupdt();
	var sendData = fn_cart_sendData(frm);

	$.ajax({type:"POST", url:'/cart/', data:sendData, success: function(data){ fn_cart_showData(data); }});

	return false;
}
function fn_cart_showData(data){
	
	function f(data){
		var p = data.indexOf('[[*'); if (p == -1){ return data; }
		var p2 = data.indexOf('*]]'); if (p2 == -1){ return data; }
		var count = data.slice(p+3,p2);
		var el = document.getElementById('the_box_count');
		if (el != null){ el.innerHTML = count; }
		//img
		p = data.indexOf('[[*',p2); if (p == -1){ return data; }
		p2 = data.indexOf('*]]',p); if (p2 == -1){ return data; }
		count = data.slice(p+3,p2);
		var tmp = document.getElementById('cart_box_2');
		if (tmp != null){
			var img = tmp.getElementsByTagName('img')[0];
			if (img != null){
				var s = glob_static_url+'res/img/'+((count*1==0)?'basket.jpg':'basket_full.png');
				if (img.src !== s){
					img.src = s;
				}
			}
		}
		//
		return data.slice(p2+3);
	}
	data = f(data);
	function f_tel(data){
		var p = data.indexOf('id="id_phone"'); if (p == -1){ return data; }
		p = data.lastIndexOf('<',p);
		var p2 = data.indexOf('>',p);
		var v = new Array('','','','');
		var p3 = data.indexOf('value="',p);
		if (p3 != -1 && p3 < p2){
			var p4 = data.indexOf('"',p3+7);
			v = data.slice(p3+10,p4).split('-');
		}
		
		var s = '<input type="hidden" name="phone" id="id_phone" class="hidden_phone" />\
				<div class="phone-inp">\
					<div class="phone-inp-click-area" onclick="fn_cart_tel_click(this)"></div>\
					<input type="text" name="tmp_phone1" class="phone1" maxlength="3" value="'+v[0]+'" onkeyup="fn_cart_tel_keyup(this,1)" />\
					<input type="text" name="tmp_phone2" class="phone2" maxlength="3" value="'+v[1]+'" onkeyup="fn_cart_tel_keyup(this,2)" />\
					<input type="text" name="tmp_phone3" class="phone3" maxlength="2" value="'+v[2]+'" onkeyup="fn_cart_tel_keyup(this,3)" />\
					<input type="text" name="tmp_phone4" class="phone4" maxlength="2" value="'+v[3]+'" onkeyup="fn_cart_tel_keyup(this,4)" />\
				</div>';
		data = data.slice(0,p) + s + data.slice(p2+1);
		return data;
	}
	data = f_tel(data);
	$.fancybox(data);
}
function fn_cart_tel_keyup(_this,n){
	var go_next = false;
	if (n == 1 && _this.value.length >= 3){ go_next = true; }
	if (n == 2 && _this.value.length >= 3){ go_next = true; }
	if (n == 3 && _this.value.length >= 2){ go_next = true; }
	if (go_next){
		n++;
		var inps = _this.parentNode.getElementsByTagName('input');
		for (var i = 0; i < inps.length; i++){
			if (inps[i].className === 'phone'+n){
				inps[i].focus();
				return;
			}
		}
	}
}
function fn_cart_tel_valupdt(){
	
	var _this = null;
	var els = document.getElementById('fancybox-outer').getElementsByTagName('input');
	for (var i = 0; i < els.length; i++){
		if (els[i].className === 'phone1'){
			_this = els[i];
			break;
		}
	}
	if (_this == null){ return; }
	
	
	var inps = _this.parentNode.getElementsByTagName('input');
	var val = '+7';
	for (var i = 0; i < inps.length; i++){
		if (inps[i].className.slice(0,5) === 'phone'){
			val += '-'+inps[i].value;
		}
	}
	if (val.length < 16){ val = ''; }
	$('#fancybox-outer .hidden_phone').val(val);
}
function fn_cart_tel_click(_this){
	var inps = _this.parentNode.getElementsByTagName('input');
	for (var i = 0; i < inps.length; i++){
		if (inps[i].className === 'phone1'){
			inps[i].focus();
			return;
		}
	}
}
function fn_cart_sendData(frm){

	if (frm == null){ return ''; }
	
	var sendData = '';
	
	var inps = new Array('input','textarea');

	for (var j = 0; j < inps.length; j++){
	
		var frm_inps = frm.getElementsByTagName(inps[j]);
		
		for (var i = 0; i < frm_inps.length; i++){
			var name = frm_inps[i].name;
			if (name !== '' && name.slice(0,4)!=='tmp_'){
				sendData += ((sendData==='')?'':'&')+name+'='+encodeURIComponent(frm_inps[i].value);
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