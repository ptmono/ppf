    <!--
function MM_findObj(n, d) { //v4.01
    var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
	d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
    if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
    for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
    if(!x && d.getElementById) x=d.getElementById(n); return x;
}


//새창-->
function newin(width,height,url,name) {
    msgWindow=window.open(url,name,'statusbar=yes,scrollbars=yes,status=yes, location=yes, directories=yes, status=yes, toolbar=yes ,resizable=yes,width='+width+',height='+height);
}

function MM_showHideLayers() { //v3.0
    var i,p,v,obj,args=MM_showHideLayers.arguments;
    for (i=0; i<(args.length-2); i+=3) if ((obj=MM_findObj(args[i]))!=null) { v=args[i+2];
									      if (obj.style) { obj=obj.style; v=(v=='show')?'visible':(v='hide')?'hidden':v; }
									      obj.visibility=v; }
}


//-->

function MM_swapImgRestore() { //v3.0
    var i,x,a=document.MM_sr; for(i=0;a&&i<a.length&&(x=a[i])&&x.oSrc;i++) x.src=x.oSrc;
}

function MM_preloadImages() { //v3.0
    var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
				  var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
				  if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}

function MM_swapImage() { //v3.0
    var i,j=0,x,a=MM_swapImage.arguments; document.MM_sr=new Array; for(i=0;i<(a.length-2);i+=3)
    if ((x=MM_findObj(a[i]))!=null){document.MM_sr[j++]=x; if(!x.oSrc) x.oSrc=x.src; x.src=a[i+2];}
}
//-->

// Auto resizing comment area
(function(a){a.fn.autoResize=function(j){var b=a.extend({onResize:function(){},animate:true,animateDuration:150,animateCallback:function(){},extraSpace:40,limit:1000},j);this.filter('textarea').each(function(){var c=a(this).css({resize:'none','overflow-y':'hidden'}),k=c.height(),f=(function(){var l=['height','width','lineHeight','textDecoration','letterSpacing'],h={};a.each(l,function(d,e){h[e]=c.css(e)});return c.clone().removeAttr('id').removeAttr('name').css({position:'absolute',top:0,left:-9999}).css(h).attr('tabIndex','-1').insertBefore(c)})(),i=null,g=function(){f.height(0).val(a(this).val()).scrollTop(10000);var d=Math.max(f.scrollTop(),k)+b.extraSpace,e=a(this).add(f);if(i===d){return}i=d;if(d>=b.limit){a(this).css('overflow-y','');return}b.onResize.call(this);b.animate&&c.css('display')==='block'?e.stop().animate({height:d},b.animateDuration,b.animateCallback):e.height(d)};c.unbind('.dynSiz').bind('keyup.dynSiz',g).bind('keydown.dynSiz',g).bind('change.dynSiz',g)});return this}})(jQuery);

$("textarea[class=comment]").autoResize();


//var bookmark_color = {1: "#fffca6", 2: "white"};
var bookmark_color = {1: "#fffa6d", 2: "white"};

function toggle_on_click(obj) {
    var idx = jQuery(obj).find(".column_idx").text();
    var idx_color = $.jStorage.get(idx);

    if (!(idx_color)){
    	idx_color = 1;
    	$.jStorage.set(idx, 1);
    }
    else{
    	if (idx_color == 1){
    	    idx_color = 2;
    	    $.jStorage.deleteKey(idx);
    	}
    	// if (idx_color == 2){
    	//     idx_color = 2;
    	//     $.jStorage.deleteKey(idx);
    	// }
    }
    console.log(idx_color);
    obj.css("background-color", bookmark_color[idx_color]);
};

function init_job_content(obj) {

    var idx = jQuery(obj).find(".column_idx").text();
    if (!(idx)){
	return
    }

    var idx_color = $.jStorage.get(idx);

    if (!(idx_color)){
	return
    }
    obj.css("background-color", bookmark_color[idx_color]);
}


// scrolling

var g_page_count = 1;

function scrollOnce() {
    window.g_page_count = window.g_page_count + 1;
	
    var surl = "job/page/" + window.g_page_count.toString();
    $('div#loadmoreajaxloader').show();
    $.ajax({
        url: surl,
        success: function(html)
        {
            if(html)
            {
		
		$('div#more_jobs_button').hide();
                $('div#loadmoreajaxloader').fadeIn();
		var delay = 0;
                $("div#ajax_more_jobs").append(html).delay().animate({opacity:1}, 200);
		delay += 100;
		$('div#loadmoreajaxloader').fadeOut();
		$('div#more_jobs_button').show();
            }else
            {
		$('div#more_jobs_button').hide();		
                $('div#loadmoreajaxloader').fadeIn();
                $('div#loadmoreajaxloader').html('<center>No more posts to show.</center>');
            }
	    $(".column").each(function () {
		init_job_content($(this));
	    });

        },
    });

}

// Login, Sign up

function ddlogin() {
    var curl = $(location).attr('href');
    var surl = "/login?next=" + curl;
    var email = $('#email').val();
    var password = $('#password').val();
    $.ajax({
	url: surl,
	type: "POST",
	data: {email: email, password: password},
	success: function(html)
	{
	    if (html.substring(1,4) == "div"){
	    	open_login_form(html);
	    } else {
		var newDoc = document.open("text/html", "replace");
		newDoc.write(html);
		newDoc.close();
	    }
	},
    });
};

function ddsignup() {
    var curl = $(location).attr('href');
    var surl = "/join?next=" + curl;
    var email = $('#email').val();
    var password = $('#password').val();
    var confirm = $('#confirm').val();
    console.log(curl);
    $.ajax({
	url: surl,
	type: "POST",
	data: {email: email, password: password, confirm: confirm},
	success: function(html){
	    if (html.substring(1,4) == "div"){
		open_sign_form(html);
	    } else {
		var newDoc = document.open("text/html", "replace");
		newDoc.write(html);
		newDoc.close();
	    }
	},
    });
}

function open_sign_form(html){
    var x = $(window).width()/2;
    x = x - 200;
    $('#admin_popup').html(html);    
    $('#admin_popup').bPopup({
	position: [x, 100]
    });
    $('div.txt-fld').keypress(function(e) {
	if (e.which == 13) {
	    ddsignup();
	    return false;
	}
    });

    $('#sign_submit').on("click", function () {
	ddsignup();
    });

    $('#email').focus();
}

function open_login_form(html){
    var x = $(window).width()/2;
    x = x - 200;
    $('#admin_popup').html(html);    
    $('#admin_popup').bPopup({
	position: [x, 100]
    });
    $('#form_email, #form_passwd').keypress(function(e) {
	if (e.which == 13) {
	    ddlogin();
	    return false;
	}
    });
    $('#login_sign_submit').on("click", function () {
	ddsignup();
    });
    $('#login_submit').on("click", function () {
	ddlogin();
    });

    $('#email').focus();

}


function infinit_scrolling() {
    if($(window).scrollTop() > $(document).height() - $(window).height() - 120)
    {
    	scrollOnce();
    }
};

// $(".column").one("click", function () {
//     $(this).css("background-color", "red");
// });

// $(document).ready(function () {
//     $("#column").on("click", function () {
// 	$(this).css("background-color", "red");
//     });
// });

// $(".column").click(function () {
//     toggle_on_click($(this));
// });

$("body").on("click", ".column", function () {
    toggle_on_click($(this));
});

$('#login_button').on("click", function () {
    ddlogin();
});

$(".column").each(function () {
    init_job_content($(this));
});

var throttled = _.throttle(infinit_scrolling, 400);
$(window).scroll(throttled);


$(window).scroll(function(){
    $('div.user_info').css({
	'top': $(this).scrollTop() + 15
    });
});

