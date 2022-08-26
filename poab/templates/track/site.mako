<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <link rel="stylesheet" href="/static/css/ol/ol_common.css" type="text/css">
    <link rel="stylesheet" href="/static/css/ol/ol.css" type="text/css">
    <script src="/static/js/ol/OpenLayers.js"></script>
    <!--    <script src="https://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script> -->
    <%include file="/track/map.js" />
    <link rel="shortcut icon" href="/static/images/bicycle.ico" />
    <title>poab.org - map</title>
  </head>
  <body onload="init()">
    ${self.body()}
  </body>
</html>
