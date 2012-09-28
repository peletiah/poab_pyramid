<%def name="pages()">
    <div class="pages">
        <%
            controller=request.matched_route.name.split(':')[0]
            action_type=action
            id1=id
            i=0
            j=1
            pagestring=''
            fastrewind_page=''
            fastforward_page=''
            if curr_page > 4 and len(pages_list)>9:
                i=curr_page-4
                j=curr_page-3
            
            
            kl_key='''<span class="page_arrow hoverhide"><a title="Use the h/l- and j/k-keys to navigate"><span class="keyboard-key">k</span> &#8593;</a></span><span class="page_arrow hoverhide"><a title="Use the h/l- and j/k-keys to navigate"><span class="keyboard-key">l</span> &#8594;</a></span>'''
            hj_key='''<span class="page_arrow hoverhide"><a title="Use the h/l- and j/k-keys to navigate"><span class="keyboard-key">j</span> &#8595;</a></span><span class="page_arrow hoverhide"><a title="Use the h/l- and j/k-keys to navigate"><span class="keyboard-key">h</span> &#8592;</a></span>'''
            prev_page='''<span class="page_arrow"><a class="prev_page" href="/%s/%s/%s/%s" title="older entries" ><span>older</span> &#8594;</a></span>'''% (controller,action_type,id1,str(curr_page-1))
            next_page='''<span class="page_arrow"><a class="next_page" href="/%s/%s/%s/%s" title="newer entries" >&#8592; <span>newer</span></a></span>'''% (controller,action_type,id1,str(curr_page+1))
             
            
            
       ###FASTREWIND
            if len(pages_list)<=9:
                fastrewind_page=''
            elif curr_page<10 and curr_page>4:
                fastrewind_page=''' <a href="/%s/%s/%s/%s" title="Photos page %s" >...</a>''' % (controller,action_type,id1,str(0),str(1))
            elif curr_page>4:
                fastrewind_page=''' <a href="/%s/%s/%s/%s" title="Photos page %s" >...</a>''' % (controller,action_type,id1,str(curr_page-9),str(curr_page-8))
            pagestring=fastrewind_page+pagestring
### 
            
            for page in pages_list:
                #don't display more pages than total
                if j>len(pages_list):
                    continue
                elif i==curr_page:
                    pagestring=''' <b>%s</b> %s'''% (str(j),pagestring)
                elif j<10:
                    pagestring=''' <a href="/%s/%s/%s/%s" title="Photos page %s" >%s</a> %s'''% (controller,action_type,id1,str(i),str(j),str(j),pagestring)
                #don't display more than 5 extra pages
                elif j> curr_page+5 and j>5:
                    continue
                else:
                    pagestring=''' <a href="/%s/%s/%s/%s" title="Photos page %s" >%s</a> %s'''% (controller,action_type,id1,str(i),str(j),str(j),pagestring)
                i=i+1
                j=j+1
            
###FASTFORWARD       
            if len(pages_list)<9:
                fastforward_page=''
            elif curr_page+9<len(pages_list):
                fastforward_page=''' <a href="/%s/%s/%s/%s" title="Photos page %s" >...</a>''' % (controller,action_type,id1,str(curr_page+9),str(curr_page+10))
            #if we are less than 6 pages from the last page, we don't view a jump anymore
            elif curr_page+6==len(pages_list):
                fastforward_page=''
            #if we are less than 9 pages from the last page, we jump to the last page
            else:
                fastforward_page=''' <a href="/%s/%s/%s/%s" title="Photos page %s" >...</a>''' % (controller,action_type,id1,str(len(pages_list)-1),str(len(pages_list)))
###
            
            if curr_page+5<len(pages_list) and len(pages_list)>9:
                pagestring=''' <a href="/%s/%s/%s/%s" title="Photos page %s" >%s</a> %s %s'''% (controller,action_type,id1,str(len(pages_list)-1),str(len(pages_list)),str(len(pages_list)),fastforward_page,pagestring)
            
            if curr_page>4 and len(pages_list)>9:
                pagestring=pagestring+''' <a href="/%s/%s/%s/%s" title="Photos page %s" >%s</a> '''% (controller,action_type,id1,str(0),str(1),str(1))
            
            
            
            if curr_page>0:
                pagestring=pagestring+prev_page
            
            if curr_page<(len(pages_list)-1):
                pagestring=next_page+pagestring
            
            if curr_page>0 and curr_page<(len(pages_list)-1):
                pagestring=hj_key+pagestring+kl_key
             
            if len(pages_list)==1:
                pagestring=''
        %>
        ${pagestring | n}
    <br>
       &nbsp;
    </div>
</%def>
