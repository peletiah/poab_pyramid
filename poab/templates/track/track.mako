<%inherit file="site.mako" />
%if action!='infomarker' and action!='simple' and action!='fromgpx': 
<%include file="/menu/menu_map.mako" />
%endif
<div id="mapdiv" class="fullscreenmap"></div>

