<%namespace name="pages" file="/misc/pages.mako"/>
<%inherit file="site.mako" />
<%include file="/menu/menu.mako" />
<div class="view_content">

${pages.pages()}

<% i=1 %>
% for viewdetail in viewlist:
<div class="view">
<div class="hentry">
<h2>
<a class="entry-title" id="/view/id/${viewdetail.photoid}" name='${i}' href="#"></a>
</h2>
</div>
<% i=i+1 %>
<div class="imagecontainer">
    <a rel="map_colorbox" href="/track/simple/${viewdetail.trackpointinfo.id}/${viewdetail.photoid}" title="View photolocation on map"><img class="image" src="/static${viewdetail.location}990/${viewdetail.name}" /></a>
    <div class="caption">
         <span class="caption_left">
            % if viewdetail.image.image_flickr_ref:
            <span>&#8594;</span>
            <a href="http://www.flickr.com/peletiah/${viewdetail.image.image_flickr_ref[0].photoid}" target="_blank" title="View photo on flickr">www.flickr.com</a><br />
            % endif
            <span>&#8594;</span>
            <a rel="map_colorbox" href="/track/simple/${viewdetail.trackpointinfo.id}/${viewdetail.photoid}" title="View photolocation on map">view on map</a>
        </span>
        <span class="caption_center">
            % if viewdetail.comment:
                <a href="/log/id/${viewdetail.log[0].id}" title="Show log for this image">${viewdetail.comment | n}</a>
            % elif viewdetail.title:
                <a href="/log/id/${viewdetail.log[0].id}" title="Show log for this image">&ldquo;${viewdetail.title}&rdquo;</a>
            % endif            
            <br />
            % if viewdetail.trackpointinfo.location_ref:
            ${viewdetail.trackpointinfo.location_ref[0].name},
            % endif
            % if viewdetail.trackpointinfo.temperature==None:
            n/a,
            % else:
            ${viewdetail.trackpointinfo.temperature}&#8451,
            % endif
            % if viewdetail.trackpointinfo.altitude==None:
            n/a
            % else:
            ${viewdetail.trackpointinfo.altitude}m
            % endif
        </span>
        <span class="caption_right">
            ${viewdetail.localtime} (<a href="" title="${viewdetail.timezone.description}, ${viewdetail.utcoffset}">${viewdetail.timezone.abbreviation})</a><br />
            ${viewdetail.focal_length}&nbsp;|&nbsp;f${viewdetail.aperture}&nbsp;|&nbsp;${viewdetail.shutter}s
        </span>
    

    </div>
</div>
</div>
% endfor

<a name='bottom' href="#"></a>
${pages.pages()}



</div>
<script>
$(".caption").hide();
$("div.imagecontainer").mouseover(function(){
      $(".caption",this).show();
      width=($("img[class='image']",this).width())
      $('div.imagecontainer').css({width: width});
    }).mouseout(function(){
      $(".caption",this).hide();
    });

$(".hoverhide").hide();
$("div.pages").mouseover(function(){
      $(".hoverhide",this).show();
    }).mouseout(function(){
      $(".hoverhide",this).hide();
    });


modMenu(${id});

$(document).ready(function(){
    $("a[rel='map_colorbox']").colorbox({transition:"fade", width:"952px", height:"584px", iframe:true});
        });
</script>



