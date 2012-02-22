/* Ajax Django CSRF */
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

$(function() {
    $( ".set" ).buttonset();
    $( ".ch" ).button();
});

$(document).ready(function () {
    lines();
    var $create_edit = $('#create_edit');
    var $create_edit_block = $('#create_edit_block');
    var clid, url, $target_client;
    var $create_bg = $('#create_bg');
    $('.test_id').change(function () {
        var value = $(this).val();
        $.post("/myadmin/test_json/", {param: value});
    });
    $('.test_id').each(function(){
        var $thisis = $(this).parents('.action');
        $(this).find('option').each(function(){
            var copy_wrap = $(this).clone().appendTo($thisis.find('.ps_selector')).wrap('<li></li>').wrapInner('<p class="'+$(this).val()+'"></p>').find('p').unwrap();
            //copy_wrap.css({background:'red'});
        });
    });
    $('.ps_selector li').live('click',function(){
        var $this_li_p = $(this).parents('.action').children('span').children('p');
        var value = $(this).children('p').attr('class');
        $(this).parents('.action').children('span').children('p').text($(this).children('p').text());
        $.post("/myadmin/test_json/", {param: value}, function(){
            //alert('!');
            invisible($this_li_p);
        });
    });
    //редактирование клиента
    var isnew = false;
    $('.items_list .name a').live('click',function(){
        $('.clientedit').remove();
        $target_client = $(this).parents('tr');
        var oftop = $create_edit.fadeIn().css({position:'fixed',top:'0'}).children('#create_edit_block').html('<span class="load">Загруза...</span>').offset().top;
        $create_bg.fadeIn();
        clid = parseFloat($(this).parents('tr').find('.id').text(),10);
        url = '/myadmin/client/'+clid+' #client_edit_form';
        //alert(url);
        $create_edit_block.load(url,function(){
            $create_edit.fadeIn().css({position:'absolute',top:oftop});
            $create_edit_block.children('.load').hide().end().find('#client_edit_form').slideDown().attr('action','/myadmin/client/'+clid+'/');
            $('#delite_client').attr('href','/myadmin/client/'+clid+'/delete');
            $('#new_order').attr('href','/myadmin/client/'+clid+'/copy');
            $(".chzn-select").chosen();

        });
        isnew = false;
        return false;
    });
    $('#create_edit .close').click(function(e){
        $('#create_edit').fadeOut();
        $create_bg.fadeOut(100);
    });
    //удаление
    $('#delite_client').live('click',function(){
        $.get('/myadmin/client/'+clid+'/delete',function(){

        });
        $create_edit.hide();
        $create_bg.fadeOut(100,function(){
            $target_client.fadeOut(1500,function(){
                $(this).remove()
            });
        });
        return false;
    });
    //добавление нового клиента
    $('.lt_un .icon_man').live('click',function(){
        $('.clientedit').remove();
        $target_client = $(this).parents('tr');
        var oftop = $create_edit.fadeIn().css({position:'fixed',top:'0'}).children('#create_edit_block').html('<span class="load">Загруза...</span>').offset().top;
        $create_bg.fadeIn();
        url = "/myadmin/client/add #client_edit_form"
        $create_edit_block.load(url,function(){
            $create_edit.fadeIn().css({position:'absolute',top:oftop});
            $create_edit_block.children('.load').hide().end().find('#client_edit_form').slideDown().attr('action','/myadmin/client/add');
            $(".chzn-select").chosen();
        });
        isnew = true;
        return false;
    });
    //Отправка данных
    $('#client_edit_form .selectbutton').live('click',function(){
        $('#client_edit_form').ajaxForm(function(msg){
            if(isnew){
                if($('#id_name').val() == ''){
                    $('#id_name').parents('tr').find('label').css({color:'red'});
                    window.scroll(0,0);
                }else if($('#id_phone').val() == ''){
                    $('#id_phone').parents('tr').find('label').css({color:'red'});
                    window.scroll(0,0);
                }else{
                    url = '../client/'+msg+'/get .item td';
                    $create_edit.hide();
                    $create_bg.fadeOut(100);
                    $('.items_list tbody').prepend('<tr class="item"></tr>').find('tr').eq(0).load(url,function(){
                        var $thisis = $target_client.find('.action');
                        $(this).css({opacity:0}).animate({opacity:1},2000);
                        $target_client.find('option').each(function(){
                            //$(this).clone().appendTo($thisis.find('.ps_selector')).wrap('<li></li>');
                            $(this).clone().appendTo($thisis.find('.ps_selector')).wrap('<li></li>').wrapInner('<p class="'+$(this).val()+'"></p>').find('p').unwrap();
                        });
                        invisible($thisis.children('span').children('p'));
                        lines();
                    });
                }
            }else{
                if($('#id_name').val() == ''){
                    $('#id_client-name').parents('tr').find('label').css({color:'red'});
                    window.scroll(0,0);
                }else if($('#id_client-phone').val() == ''){
                    $('#id_phone').parents('tr').find('label').css({color:'red'});
                    window.scroll(0,0);
                }else{
                    url = '../client/'+clid+'/get .item td';
                    $create_edit.hide();
                    $create_bg.fadeOut(100);
                    //alert(url);
                    $target_client.load(url,function(){
                        var $thisis = $target_client.find('.action');
                        $target_client.find('option').each(function(){
                            //$(this).clone().appendTo($thisis.find('.ps_selector')).wrap('<li></li>');
                            $(this).clone().appendTo($thisis.find('.ps_selector')).wrap('<li></li>').wrapInner('<p class="'+$(this).val()+'"></p>').find('p').unwrap();
                        });
                        invisible($thisis.children('span').children('p'));
                        lines();
                    });
                }
            }

            // window.location.reload("");
        });
    });
    function invisible($intarg){
        var str = $intarg.text();
        var regText = ""+str+".(\\d+).";
        //alert(str);
        var reg = new RegExp(regText);
        //alert(reg);
        $('#accordion .ui-button-text span').each(function(){
            if(reg.test($(this).text())){
                //alert($(this).parents('li').find('input').attr('checked'));
                if(!($(this).parents('li').find('input').attr('checked'))){
                    $intarg.parents('tr').fadeOut(1000);
                }
            }
        });

    }
    var dsdfsfd;

    $('.action>span>p').live('click',function(){
        $('.ps_selector').hide();
        dsdfsfd = this;
        $(this).parents('span').children('.ps_selector').show().addClass('active_selector_ps');
    });
    $('body').click(function(e){
        //	alert(e.target);
        //	alert(dsdfsfd);
        if(e.target != dsdfsfd){
            $('.active_selector_ps').hide();
        }
    });
});

function lines(){
    $('.items_list tr:even').css({background:'#fff'});
}
