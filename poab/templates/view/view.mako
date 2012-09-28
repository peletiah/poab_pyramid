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
    <!--<a href="/view/id/${viewdetail.photoid}" title="View photo by itself"><img class="image" src="http://farm${viewdetail.flickrfarm}.static.flickr.com/${viewdetail.flickrserver}/${viewdetail.flickrphotoid}_${viewdetail.flickrsecret}_b.jpg" /></a>-->
    <!--<a rel="map_colorbox" href="/track/simple/${viewdetail.trackpointinfo.id}/${viewdetail.photoid}" title="View photolocation on map"><img class="image" src="http://farm${viewdetail.flickrfarm}.static.flickr.com/${viewdetail.flickrserver}/${viewdetail.flickrphotoid}_${viewdetail.flickrsecret}_b.jpg" /></a>-->
    <a rel="map_colorbox" href="/track/simple/${viewdetail.trackpointinfo.id}/${viewdetail.photoid}" title="View photolocation on map"><img class="image" src="/static${viewdetail.imgname}" /></a>
    <div class="caption">
         <span class="caption_left">
            <span>&#8594;</span>
            <a href="http://www.flickr.com/peletiah/${viewdetail.flickrphotoid}" target="_blank" title="View photo on flickr">www.flickr.com</a><br />
            <span>&#8594;</span>
            <a rel="map_colorbox" href="/track/simple/${viewdetail.trackpointinfo.id}/${viewdetail.photoid}" title="View photolocation on map">view on map</a>
        </span>
        <span class="caption_center">
                        % if viewdetail.description:
                <a href="/log/id/${viewdetail.log_id}" title="Show log for this image">${viewdetail.description | n}</a>
            % else:
                <a href="/log/id/${viewdetail.log_id}" title="Show log for this image">&ldquo;${viewdetail.title}&rdquo;</a>
            % endif            
            <br />
            ${viewdetail.trackpointinfo.location},
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
            ${viewdetail.focal_length}&nbsp;|&nbsp;${viewdetail.aperture}&nbsp;|&nbsp;${viewdetail.shutter}
        </span>
    

    </div>
</div>
</div>
% endfor

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



