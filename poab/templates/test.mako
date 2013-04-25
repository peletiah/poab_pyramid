${bla}<br />
${blu}<br />
${page}<br />
${request.matched_route.name}<br />
${request.route_url('test')}<br />
<% controller = request.matched_route.name.split(':')[0] %>
${controller}
