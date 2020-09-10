from __future__ import absolute_import
import string


def sub_doc(s, pos, n, search_expr):
    # s   - the string
    # pos - position in string
    # n   - number of chars to show before and after pos
    start_ix = int(pos) - int(n)
    if start_ix < 0:
        start_ix = 0
    end_ix = int(pos) + int(n) + len(search_expr)
    if end_ix > len(s):
        end_ix = len(s)
    ret = string.replace(s[start_ix:end_ix], '<', ' ')
    ret = string.replace(ret, '>', ' ')
    return string.replace(string.lower(ret), string.lower(search_expr),
                          '<b><u>' + search_expr + '</u></b>')


def fast_site_search(self, search_expr='', cnt=0):
    ret = ''
    count = cnt
    lowsearch = string.lower(search_expr)  # Friends in low places
    for i in self.objectItems(['Folder','ZWiki Page', 'DTML Document',
                               'Yihaw Folder', 'Yihaw News Item','Yihaw URL']):
      o = i[1] # the object
      id = i[0]
      if o.getNodeName() in ("Folder","Yihaw Folder"):
            ret1,count1=fast_site_search(o,search_expr,count)
            ret=ret+ret1
            count=count1
      else:
        found=None
	fcurr = []
	for curr in ('title','raw','description','details','note'):
	  if not o.hasProperty(curr):
	      continue
	  prop=''
	  if o.getPropertyType(curr) in ("string","text"):
	      prop=o.getProperty(curr)
          ix1 = string.find(string.lower(prop),lowsearch) #prop
          if search_expr=='' or  ix1 != -1:
	     fcurr.append(curr)
	     found=prop
             count=count+1
	if found:
             ret=ret+'<img src="'
             if o.hasProperty('ico'): ret=ret+self.iconspath+o.ico
             else: ret=ret+o.icon
             ret=ret+'" border=0 width=18 height=16>' + \
	      repr(fcurr) + '<a href="'+o.absolute_url()
             if hasattr(o, 'item_info'):
               if o.item_info=='LocalForum': ret=ret+'/view_item'
               if o.item_info=='WikiForum': ret=ret+'/view_doc'
               if o.item_info=='IForum': ret=ret+'/../view_item?doc_id='+id
               if o.item_info=='News': ret=ret+'/view_news'
             ret=ret+'">'+o.title_or_id()+'</a>'
             if search_expr!='':
               ret=ret+'<div style="margin-left:0.5cm; position:relative; text-align : left;">'
               if ix1!=-1: ret=ret+sub_doc(found,ix1,400,search_expr)
               ret=ret+'</div><hr>'
             else: ret=ret+'<br>'
  return ret,count
