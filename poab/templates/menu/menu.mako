<%namespace name="hostname" file="/misc/hostname.mako"/>
<link rel="alternate" type="application/atom+xml" href="http://poab.org/feed" title="POAB.org - World Cycle Blog" />
<link rel="stylesheet" type="text/css" href="/static/css/main.css" media="screen">
<link type="text/css" rel="Stylesheet" media="screen" href="/static/css/flora.datepicker.css"/>
<link rel="stylesheet" href="/static/css/jquery.autocomplete.css" type="text/css" />
<link type="text/css" rel="Stylesheet" media="screen" href="/static/css/colorbox.css"/>
<link href="/static/css/caption.css" media="screen" rel="stylesheet" title="" type="text/css"/>
<script src="/static/js/jquery-1.3.2.js" type="text/javascript"></script>
<!--<script src="/static/js/jquery_plugins/ui.core.js" type="text/javascript"></script>-->
<script src="/static/js/graph/flot_0.6/jquery.flot.js" type="text/javascript"> </script>
<script type="text/javascript" src="/static/js/jquery_plugins/colorbox/jquery.colorbox.js"></script>
<script type="text/javascript" src="/static/js/paging_keys_js/paging_keys.js"></script>
<!--[if IE]><script language="javascript" type="text/javascript" src="excanvas.pack.js"></script><![endif]-->
<script type="text/javascript">
    
hostname = "${hostname.hostname()}"
            $(document).ready(function(){
                $("a[rel='image_colorbox']").colorbox({transition:"fade", photo:"true", height: "95%"});
                $("a[rel='map_colorbox']").colorbox({transition:"fade", width:"952px", height:"584px", iframe:true});
        });
function showNavigation(navcontent) {
        $(navcontent).replaceAll(".navigation");
    };

function modMenu(country_id) {
        $(".menu").attr("href", function() {
            var re = new RegExp("(http://w{0,3}\.{0,1}"+hostname+"/[A-z]{1,}/)");
            //var m = re.exec(this.href)
            //alert(m);
            //alert(this.href) 
            return(this.href.replace(re, "$1c/"+country_id));
        });
    }
    
    function resetMenu(country_id) {
        $(".menu").attr("href", function() {
            var re = new RegExp("(http://w{0,3}\.{0,1}"+hostname+"/[A-z]{1,}/)c/[0-9]{1,}");
            return(this.href.replace(re, "$1c/0"));
        });
    }

    function markMenu() {
        var re = new RegExp("http://w{0,3}\.{0,1}"+hostname+"/([A-z]{1,})");
        m = re.exec(document.URL)
        $(".menu").attr("href", function() {
            mm=re.exec(this.href)
            if (m!=null && mm!=null) {
              if (m[1]==mm[1]) {
                $(this).css("background","#00607f");
                $(this).css("-webkit-border-radius","5px");
                $(this).css("-moz-border-radius","5px");
                $(this).css("border-radius","5px");
              };
            }
            else if (m==null && mm!=null) {
                if (mm[1]=="log") {
                  $(this).css("background","#00607f");
                  $(this).css("-webkit-border-radius","5px");
                  $(this).css("-moz-border-radius","5px");
                  $(this).css("border-radius","5px");
                };
            };
        });
        }

function showSubcontent(contentlink) {
   $.ajax({
       url: contentlink,
       cache: true,
       success: function(response) { 
         $(".subcontent").replaceWith('<div class="subcontent">' + response + '</div>');
           }
        
   });
    }
        </script>
<div id="menublock">
	<ul class="menucontent" class="clearfix">
	    <li class="menuli"><a class="menu" href="/log">journal</a></li>
	    <li class="menuli"><a class="menu" href="/view">photos</a></li>
	    <li class="menuli"><a class="menu" href="/track">map</a></li>
<!--	    <li class="menuli"><a class="menu" href="/facts">stats</a></li>-->
	    <li class="menuli"><a class="menu" href="/about">about</a></li>
<!--       <li class="navigation">
         <ul>
            <li class="navli">
                <a href="#" title="Show all entries" onclick='resetContent();'>All</a>
            </li>-->
             <!--<li class="navli">
                <a href="#" title="Show all entries" onclick='resetContent();'>justtesting</a>
            </li>-->
<!--          </ul>
        </li>
	    <li class="menu_nodecoration">
            <a class="menu" href="http://poab.org/feed" target="_blank"><img src="/static/images/icons/rss.png" /></a>
        </li>-->
	</ul>
</div>
<script type="text/javascript">
markMenu();
</script>
