<%namespace name="pages" file="/misc/pages.mako"/>
<%inherit file="site.mako" />
<%include file="/menu/menu.mako" />
<div class="content">

<% j=len(logdetaillist) 
i=1
%>

<!--<div class="subcontent">
</div>-->
<div class="log" "clearfix">
${pages.pages()}

        % for log in logdetaillist:
            % if log.twitter==True:
                <div class="twitter">
                    <div class="hentry">
                        <h2>
                            <a class="entry-title" href="#" name=${i}></a>
                        </h2>
                    </div>
                    <% i=i+1 %>
                    <div class="logheader">
                        <span class="logheader_left">${log.created}</span>
                        <span class="logheader_right"><a  rel="map_colorbox" href="/track/simple/${log.infomarkerid}" title="View location of this entry on a map">${log.location}</a></span>
                    </div>
                    <div class="twittercontent">
                         ${log.content | n}
                    </div>
                    <span class="twitter_icon">
                         <a href="http://twitter.com/derreisende/statuses/${log.guid | n}" target="_blank"></a>
                    </span>
                </div>
            % else:
            <div class="logdetail">
                    <div class="hentry">
                        <h2>
                            <a class="entry-title" href="#" name=${i}></a>
                        </h2>
                    </div>
                <% i=i+1 %>
                <div class="logheader">
                    <span class="logheader_left">${log.created}</span>
                    <span class="logheader_right"><a  rel="map_colorbox" href="/track/simple/${log.infomarkerid}" title="View location of this entry on a map">${log.location}</a></span>
                </div>
                <div class="logcontent">
                    <h2><a href="/log/id/${log.id}" title="Permanent link to this journal-entry">${log.topic}</a></h2>
                    <div class="author">by <a href="about#${log.author.name}">${log.author.displayname}</a>, published on ${log.published}</div>
                    <h3>
                    % if log.distance==None:
                        
                    % else:
                        <b>distance:</b> ${log.distance}<br>
                    % endif
                    % if log.timespan==None:
                        
                    % else:
                        <b>duration:</b> ${log.timespan}<br>
                    % endif
                    </h3>
                    <div class="logdetail_icons">
                        ${log.gallerylink | n}
                        % if log.distance==None:
                        
                        % else:
                            <span class="track_icon"><a title="Show route on map" rel="map_colorbox" href="/track/infomarker/${log.infomarkerid}"></a></span>
                            <!--<span class="stats_icon"><a title="Show statistics for this day" href="/facts/stats/${log.infomarkerid}"></a></span>-->
                        % endif
                    </div>
                    <div class="logtext">
                    ${log.content | n}
                    </div>
                </div>
                <span class="txt_icon">
                    <a href="/log/id/${log.id}" title="Permanent link to this journal-entry"></a>
                </span>
                % if j>1:
                <!--    <div class="updown">
                        <a href="#1" id="ud_newer" title="newer">&#8593;</a><br/>
                        <a href="#${i}" id="ud_older" title="older">&#8595;</a>
                        <a href="#${i}" id="ud_prev_page" title="older">&#8592;</a>
                        <a href="#${i}" id="ud_next_page" title="older">&#8594;</a>
                    </div>-->
                % endif


            </div>
            % endif
        % endfor
<a name="bottom" href="#"></a>
${pages.pages()}

</div>

</div>

<script type="text/javascript">
var i=0;
$(".caption").hide();
$("div.imagecontainer").mouseover(function(){ 
      $(".caption",this).show();
      width=($("img[class='inlineimage']",this).width())
      $('div.imagecontainer').css({width: width});
 }).mouseout(function(){
      $(".caption",this).hide();
    });
showSubcontent('/misc/country_svg/'+${country.iso_numcode});
function captionSize(){
      width=($(".inlineimage").css("width"))
      $('div.imagecontainer').css({width: width});
};

$(".hoverhide").hide();
//$("div.pages").mouseover(function(){
 //     $(".hoverhide",this).show();
 //   }).mouseout(function(){
//      $(".hoverhide",this).hide();
//    });

$(document).ready(function(){
        $("a[rel='image_colorbox']").colorbox({transition:"fade", photo:"true", height: "95%"});
    captionSize()
    });
$(document).ready(function(){
    $("a[rel='map_colorbox']").colorbox({transition:"fade", width:"952px", height:"584px", iframe:true});
        });
</script>

