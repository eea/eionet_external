#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2006 Søren Roug, European Environment Agency
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import zipfile
from os import unlink
from xml.sax import make_parser,handler
from xml.sax.xmlreader import InputSource
import xml.sax.saxutils
from cgi import escape

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


ANIMNS="urn:oasis:names:tc:opendocument:xmlns:animation:1.0"
CHARTNS="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
CONFIGNS="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
DCNS="http://purl.org/dc/elements/1.1/"
DR3DNS="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
DRAWNS="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
FONS="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
FORMNS="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
MATHNS="http://www.w3.org/1998/Math/MathML"
METANS="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
NUMBERNS="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
OFFICENS="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
PRESENTATIONNS="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
SCRIPTNS="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
SMILNS="urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0"
STYLENS="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
SVGNS="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
TABLENS="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
TEXTNS="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
XFORMS="http://www.w3.org/2002/xforms"
XLINKNS="http://www.w3.org/1999/xlink"


class TagStack:
    def __init__(self):
        self.stack = []

    def push(self, tag, attrs):
        self.stack.append((tag, attrs))

    def pop(self):
        item = self.stack.pop()
        return item

    def stackparent(self):
        item = self.stack[-1]
        return item[1]

    def rfindattr(self, attr):
        """ Find a tag with the given attribute """
        for tag, attrs in self.stack:
            if attrs.has_key(attr):
                return attrs[attr]
        return None
    def count_tags(self, tag):
        c = 0
        for ttag, tattrs in self.stack:
            if ttag == tag: c = c + 1
        return c

#-----------------------------------------------------------------------------
#
# ODFCONTENTHANDLER
#
#-----------------------------------------------------------------------------

class ODFContentHandler(handler.ContentHandler):
    """ The ODFContentHandler parses an ODF file and produces XHTML"""

    def wlines(self,s):
        if s != '': self.lines.append(s)

    def __init__(self):
        self.lines = []
        self.wfunc = self.wlines
        self.data = []
        self.tagstack = TagStack()
        self.pstack = []
        self.processelem = True
        self.processcont = True
        self.listtypes = {}
        self.headinglevels = [0, 0,0,0,0,0, 0,0,0,0,0] # level 0 to 10

        self.fontdict = {}
        self.currentfont = None

        # Footnotes and endnotes
        self.notedict = {}
        self.currentnote = 0
        self.notebody = ''

        self.metatags = []

        # Tags
        self.elements = {
        (DCNS, 'title'): (self.s_processcont, self.e_dc_title),
        (DCNS, 'language'): (self.s_processcont, self.e_dc_contentlanguage),
        (DCNS, 'creator'): (self.s_processcont, self.e_dc_metatag),
        (DCNS, 'description'): (self.s_processcont, self.e_dc_metatag),
        (DCNS, 'date'): (self.s_processcont, self.e_dc_metatag),
        (DRAWNS, 'frame'): (self.s_draw_frame, self.e_draw_frame),
        (DRAWNS, 'image'): (self.s_draw_image, self.donothing),
        (METANS, 'keyword'): (self.s_processcont, self.e_dc_metatag),
        (METANS, 'generator'):(self.s_processcont, self.e_dc_metatag),
        (NUMBERNS, "boolean-style"):(self.s_ignorexml, self.donothing),
        (NUMBERNS, "currency-style"):(self.s_ignorexml, self.donothing),
        (NUMBERNS, "date-style"):(self.s_ignorexml, self.donothing),
        (NUMBERNS, "number-style"):(self.s_ignorexml, self.donothing),
        (NUMBERNS, "text-style"):(self.s_ignorexml, self.donothing),
        (OFFICENS, "automatic-styles"):(self.donothing, self.donothing),
        (OFFICENS, "body"):(self.s_office_body, self.e_office_body),
        (OFFICENS, "document-content"):(self.s_office_document_content, self.e_office_document_content),
        (OFFICENS, "forms"):(self.s_ignorexml, self.donothing),
        (OFFICENS, "master-styles"):(self.s_ignorexml, self.donothing),
        (OFFICENS, "meta"):(self.s_ignorecont, self.donothing),
        (OFFICENS, "scripts"):(self.s_ignorexml, self.donothing),
        (OFFICENS, "styles"):(self.s_office_styles, self.donothing),
        (STYLENS, "graphic-properties"):(self.s_style_handle_properties, self.donothing),
        (STYLENS, "paragraph-properties"):(self.s_style_handle_properties, self.donothing),
        (STYLENS, "style"):(self.s_style_style, self.e_style_style),
        (STYLENS, "default-style"):(self.s_style_default_style, self.e_style_default_style),
        (STYLENS, "font-face"):(self.s_style_font_face, self.donothing),
        (STYLENS, "page-layout"):(self.s_ignorexml, self.donothing),
        (STYLENS, "table-cell-properties"):(self.s_style_handle_properties, self.donothing),
        (STYLENS, "table-column-properties"):(self.s_style_handle_properties, self.donothing),
        (STYLENS, "table-properties"):(self.s_style_table_properties, self.donothing),
        (STYLENS, "text-properties"):(self.s_style_handle_properties, self.donothing),
        (TABLENS, 'table'): (self.s_table_table, self.e_table_table),
        (TABLENS, 'table-cell'): (self.s_table_table_cell, self.e_table_table_cell),
        (TABLENS, 'table-column'): (self.s_table_table_column, self.donothing),
        (TABLENS, 'table-row'): (self.s_table_table_row, self.e_table_table_row),
        (TEXTNS, 'a'): (self.s_text_a, self.e_text_a),
        (TEXTNS, "alphabetical-index-source"):(self.s_text_x_source, self.e_text_x_source),
        (TEXTNS, "bibliography-configuration"):(self.s_ignorexml, self.donothing),
        (TEXTNS, "bibliography-source"):(self.s_text_x_source, self.e_text_x_source),
        (TEXTNS, 'h'): (self.s_text_h, self.e_text_h),
        (TEXTNS, "illustration-index-source"):(self.s_text_x_source, self.e_text_x_source),
        (TEXTNS, 'line-break'):(self.s_text_line_break, self.donothing),
        (TEXTNS, "linenumbering-configuration"):(self.s_ignorexml, self.donothing),
        (TEXTNS, "list"):(self.s_text_list, self.e_text_list),
        (TEXTNS, "list-item"):(self.s_text_list_item, self.e_text_list_item),
        (TEXTNS, "list-level-style-bullet"):(self.s_text_list_level_style_bullet, self.e_text_list_level_style_bullet),
        (TEXTNS, "list-level-style-number"):(self.s_text_list_level_style_number, self.e_text_list_level_style_number),
        (TEXTNS, "list-style"):(self.donothing, self.donothing),
        (TEXTNS, "note"):(self.s_text_note, self.donothing),
        (TEXTNS, "note-body"):(self.s_text_note_body, self.e_text_note_body),
        (TEXTNS, "note-citation"):(self.donothing, self.e_text_note_citation),
        (TEXTNS, "notes-configuration"):(self.s_ignorexml, self.donothing),
        (TEXTNS, "object-index-source"):(self.s_text_x_source, self.e_text_x_source),
        (TEXTNS, 'p'): (self.s_text_p, self.e_text_p),
        (TEXTNS, 's'): (self.s_text_s, self.donothing),
        (TEXTNS, 'span'): (self.s_text_span, self.e_text_span),
        (TEXTNS, 'tab'): (self.s_text_tab, self.donothing),
        (TEXTNS, "table-index-source"):(self.s_text_x_source, self.e_text_x_source),
        (TEXTNS, "table-of-content-source"):(self.s_text_x_source, self.e_text_x_source),
        (TEXTNS, "user-index-source"):(self.s_text_x_source, self.e_text_x_source),
        }

    def getxhtml(self):
        return ''.join(self.lines)

    def writeout(self, s):
        if s != '':
            self.wfunc(s)

    def writedata(self):
        d = ''.join(self.data)
        if d != '':
            self.writeout(escape(d))

    def characters(self, data):
        if self.processelem and self.processcont:
            self.data.append(data)

    def handle_starttag(self, tag, method, attrs):
        method(tag,attrs)

    def handle_endtag(self, tag, attrs, method):
        method(tag, attrs)

    def startElementNS(self, tag, qname, attrs):
        self.pstack.append( (self.processelem, self.processcont) )
        if self.processelem:
            method = self.elements.get(tag, (None, None))[0]
            if method:
                self.handle_starttag(tag, method, attrs)
            else:
                self.unknown_starttag(tag,attrs)
        self.tagstack.push( tag, attrs )

    def endElementNS(self, tag, qname):
        stag, attrs = self.tagstack.pop()
        if self.processelem:
            method = self.elements.get(tag, (None, None))[1]
            if method:
                self.handle_endtag(tag, attrs, method)
            else:
                self.unknown_endtag(tag, attrs)
        self.processelem, self.processcont = self.pstack.pop()

    def unknown_starttag(self, tag, attrs):
        pass

    def unknown_endtag(self, tag, attrs):
        pass

    def donothing(self, tag, attrs=None):
        pass

    def s_ignorexml(self, tag, attrs):
        self.processelem = False

    def s_ignorecont(self, tag, attrs):
        self.processcont = False

    def s_processcont(self, tag, attrs):
        self.processcont = True

    def classname(self, attrs):
        """ Generate a class name from a style name """
        c = attrs[(TEXTNS, 'style-name')]
        c = c.replace(".","_")
        return c

#--------------------------------------------------

    def e_emptydata(self, tag, attrs=None):
        self.data = []

    def e_dc_title(self, tag, attrs):
        self.metatags.append('<title>%s</title>\n' % escape(''.join(self.data)))
        self.data = []

    def e_dc_metatag(self, tag, attrs):
        self.metatags.append('<meta name="%s" content="%s"/>\n' % (tag[1], escape(''.join(self.data))))
        self.data = []

    def e_dc_contentlanguage(self, tag, attrs):
        self.metatags.append('<meta http-equiv="content-language" content="%s"/>\n' % ''.join(self.data))
        self.data = []

    def s_draw_frame(self, tag, attrs):
        name = attrs.get((DRAWNS, 'style-name'), "")
        name = name.replace(".","_")
        style = ""
        if attrs.has_key((SVGNS,"width")):
            style = style + "width:" + attrs[(SVGNS,"width")] + ";"
        if attrs.has_key((SVGNS,"height")):
            style = style + "height:" +  attrs[(SVGNS,"height")] + ";"
        self.writeout('<div class="G-%s" style="%s">' % (name, style))

    def e_draw_frame(self, tag, attrs):
        self.writeout('</div>\n')

    def s_draw_image(self, tag, attrs):
        anchor_type = self.tagstack.stackparent()[(TEXTNS, 'anchor-type')]
        if anchor_type != "character":
            style = ' style="display: block;"'
        else:
            style = ""
        imghref = attrs[(XLINKNS,"href")]
        self.writeout('<img alt="" src="%s"%s/>' % (imghref, style))

    def s_office_body(self, tag, attrs):
        self.writedata()
        self.writeout('<style type="text/css">\n')
        self.writeout('img { width: 100%; height: 100%; }\n')
        self.writeout('p { padding: 0; margin: 0; }\n')
        for name, styles in self.styledict.items():
            # Resolve the remaining parent styles
            # Can this get into an infinite loop?
            while styles.has_key('__parent-style-name'):
                parentstyle = self.styledict[styles['__parent-style-name']].copy()
                del styles['__parent-style-name']
                for style, val in styles.items():
                    parentstyle[style] = val
                styles = parentstyle
        for name, styles in self.styledict.items():
            self.writeout("%s {\n" % name)
            for style, val in styles.items():
                self.writeout("\t%s: %s;\n" % (style, val))
            self.writeout("}\n")
        self.writeout('</style>\n')
        self.e_emptydata(tag)
        self.writeout('</head>\n')
        self.writeout('<body>\n')

    def e_office_body(self, tag, attrs):
        for key,note in self.notedict.items():
            self.writeout('<div><a name="footnote-%d"></a><sup>%s</sup>%s</div>' % (key, note['citation'], note['body']))
        self.writeout('</body>\n')

    def s_office_document_content(self, tag, attrs):
        """ First tag in the content.xml file"""
        self.writeout('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
        self.writeout('<html xmlns="http://www.w3.org/1999/xhtml">\n')
        self.writeout('<head>\n')
        self.writeout('<meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />\n')
        for metaline in self.metatags:
            self.writeout(metaline)

    def e_office_document_content(self, tag, attrs):
        """ Last tag """
        self.writeout('</html>\n')

    def s_office_styles(self, tag, attrs):
        """ This element starts the named styles.
            I don't know why I initialise the styledict here, because the
            office:automatic-styles *could* come before.
        """
        self.styledict = {}
        self.currentstyle = None

    def s_style_handle_properties(self, tag, attrs):
        if attrs.has_key((STYLENS, 'width')):
            width = attrs[(STYLENS, 'width')]
            self.styledict[self.currentstyle]['width'] = width
        if attrs.has_key((STYLENS, 'column-width')):
            width = attrs[(STYLENS, 'column-width')]
            self.styledict[self.currentstyle]['width'] = width
        for a in ( (FONS,"background-color"),
                (FONS,"border"),
                (FONS,"border-bottom"),
                (FONS,"border-left"),
                (FONS,"border-right"),
                (FONS,"border-top"),
                (FONS,"color"),
                (FONS,"font-family"),
                (FONS,"font-size"),
                (FONS,"font-style"),
                (FONS,"font-variant"),
                (FONS,"font-weight"),
                (FONS,"line-height"),
                (FONS,"margin"),
                (FONS,"margin-bottom"),
                (FONS,"margin-left"),
                (FONS,"margin-right"),
                (FONS,"margin-top"),
                (FONS,"padding"),
                (FONS,"padding-bottom"),
                (FONS,"padding-left"),
                (FONS,"padding-right"),
                (FONS,"padding-top"),
                (FONS,"text-indent")):
            if attrs.has_key(a):
                selector = a[1]
                self.styledict[self.currentstyle][selector] = attrs[a]

        if attrs.has_key( (FONS,"text-align") ):
            align = attrs[(FONS,"text-align")]
            if align == "start": align = "left"
            if align == "end": align = "right"
            self.styledict[self.currentstyle]['text-align'] = align

        if attrs.has_key( (STYLENS,"font-name") ):
            fallback = self.fontdict.get(attrs[(STYLENS,"font-name")],'Serif')
            self.styledict[self.currentstyle]['font-family'] = '"%s", %s'  % (attrs[(STYLENS,"font-name")], fallback)

    familymap = {'paragraph':'p', 'text':'span','section':'div',
                 'table':'table','table-cell':'td','table-column':'col',
                 'table-row':'tr','graphic':'graphic' }

    def s_style_default_style(self, tag, attrs):
        """ A default style is like a style on a HTML tag
        """
        family = attrs[(STYLENS, 'family')]
        family = self.familymap.get(family,'unknown')
        self.currentstyle = family
        self.styledict[self.currentstyle] = {}

    def e_style_default_style(self, tag, attrs):
        self.currentstyle = None

    def s_style_font_face(self, tag, attrs):
        """ It is possible that the HTML browser doesn't know how to
            show a particular font. Luckily ODF provides generic fallbacks
            Unluckily they are not the same as CSS2.
            CSS2: serif, sans-serif, cursive, fantasy, monospace
            ODF: roman, swiss, modern, decorative, script, system
        """
        name = attrs[(STYLENS, 'name')]
        generic = attrs.get((STYLENS, 'font-family-generic'), None)
        fallback = "sans-serif"
        if   generic == "roman": fallback = "serif"
        elif generic == "swiss": fallback = "sans-serif"
        elif generic == "modern": fallback = "monospace"
        elif generic == "decorative": fallback = "sans-serif"
        elif generic == "script": fallback = "monospace"
        elif generic == "system": fallback = "serif"
        self.fontdict[name] = fallback

    # Short prefixes for class selectors
    familyshort = {'paragraph':'P', 'text':'S','section':'D',
                 'table':'T','table-cell':'TD','table-column':'TC',
                 'table-row':'TR','graphic':'G' }

    def s_style_style(self, tag, attrs):
        """ Collect the formatting for the style.
            Styles have scope. The same name can be used for both paragraph and character styles
            Since CSS has no scope we use aprefix.
            In ODF a style can have a parent, these parents can be chained.
            We may not have encountered the parent yet, but if we have, we resolve it.
        """
        name = attrs[(STYLENS, 'name')]
        family = attrs[(STYLENS, 'family')]
        family = self.familyshort.get(family,'X')
        parent = attrs.get((STYLENS,'parent-style-name'))
        self.currentstyle = ".%s-%s" % (family, name.replace(".","_"))
        self.styledict[self.currentstyle] = {}
        if parent:
            if self.styledict.has_key(".%s-%s" % (family, parent)):
                styles = self.styledict[".%s-%s" % (family, parent)]
                for style, val in styles.items():
                    self.styledict[self.currentstyle][style] = val
            else:
                self.styledict[self.currentstyle]['__parent-style-name'] = ".%s-%s" % (family, parent)

    def e_style_style(self, tag, attrs):
        """ End this style
        """
        self.currentstyle = None

    def s_style_table_properties(self, tag, attrs):
        if attrs.has_key((STYLENS, 'width')):
            width = attrs[(STYLENS, 'width')]
            self.styledict[self.currentstyle]['width'] = width
        if attrs.has_key((TABLENS, 'border-model')):
            self.styledict[self.currentstyle]['border-collapse'] = 'collapse'

    def s_table_table(self, tag, attrs):
        c = attrs.get((TABLENS, 'style-name'), None)
        if c:
            c = c.replace(".","_")
            self.writeout('<table class="T-%s">\n' % c)
        else:
            self.writeout('<table>\n')
        self.e_emptydata(tag, attrs)

    def e_table_table(self, tag, attrs):
        self.writedata()
        self.writeout('</table>\n')
        self.e_emptydata(tag)

    def s_table_table_cell(self, tag, attrs):
        # FIXME: rowspan and colspan
        c = attrs.get((TABLENS, 'style-name'), None)
        if c:
            c = c.replace(".","_")
            self.writeout('<td class="TD-%s">' % c)
        else:
            self.writeout('<td>')
        self.e_emptydata(tag, attrs)

    def e_table_table_cell(self, tag, attrs):
        self.writedata()
        self.writeout('</td>\n')
        self.e_emptydata(tag)

    def s_table_table_column(self, tag, attrs):
        c = attrs.get((TABLENS, 'style-name'), None)
        if c:
            c = c.replace(".","_")
            self.writeout('<col class="TC-%s"/>\n' % c)
        else:
            self.writeout('<col/>\n')
        self.e_emptydata(tag, attrs)

    def s_table_table_row(self, tag, attrs):
        # FIXME: rowspan and colspan
        c = attrs.get((TABLENS, 'style-name'), None)
        if c:
            c = c.replace(".","_")
            self.writeout('<tr class="TR-%s">\n' % c)
        else:
            self.writeout('<tr>\n')
        self.e_emptydata(tag, attrs)

    def e_table_table_row(self, tag, attrs):
        self.writedata()
        self.writeout('</tr>\n')
        self.e_emptydata(tag)

    def s_text_a(self, tag, attrs):
        self.writedata()
        href = attrs[(XLINKNS,"href")].split("|")[0]
        self.writeout('<a href="%s">' % escape(href))
        self.e_emptydata(tag, attrs)

    def e_text_a(self, tag, attrs):
        self.writedata()
        self.writeout('</a>')
        self.e_emptydata(tag)

    def s_text_h(self, tag, attrs):
        level = int(attrs[(TEXTNS, 'outline-level')])
        if level > 6: level = 6 # Heading levels go only to 6 in XHTML
        if level < 1: level = 1
        self.headinglevels[level] = self.headinglevels[level] + 1
        for x in range(level + 1,10):
            self.headinglevels[x] = 0
        self.writeout('<h%s class="P-%s">' % (level, self.classname(attrs)))
        self.e_emptydata(tag)

    def e_text_h(self, tag, attrs):
        self.writedata()
        level = int(attrs[(TEXTNS, 'outline-level')])
        if level > 6: level = 6 # Heading levels go only to 6 in XHTML
        if level < 1: level = 1
        lev = self.headinglevels[1:level+1]
        outline = '.'.join(map(str,lev))
        self.writeout('<a name="%s.%s"></a>' % ( outline, escape(''.join(self.data))))
        self.writeout('</h%s>\n' % level)
        self.e_emptydata(tag)

    def s_text_line_break(self, tag, attrs):
        self.writedata()
        self.writeout('<br/>')
        self.e_emptydata(tag)

    def s_text_list(self, tag, attrs):
        """ To know which level we're at, we have to count the number
            of <text:list> elements on the tagstack.
        """
        name = attrs.get((TEXTNS, 'style-name'))
        if name:
            name = name.replace(".","_")
            level = 1
        else:
            #pdb.set_trace()
            # FIXME: If a list is contained in a table cell or text box,
            # the list level must return to 1, even though the table or
            # textbox itself may be nested within another list.
            level = self.tagstack.count_tags(tag) + 1
            name = self.tagstack.rfindattr((TEXTNS, 'style-name'))
        self.writeout('<%s class="%s_%d">' % (self.listtypes.get(name), name, level))
        self.e_emptydata(tag, attrs)

    def e_text_list(self, tag, attrs):
        self.writedata()
        name = attrs.get((TEXTNS, 'style-name'))
        if name:
            name = name.replace(".","_")
            level = 1
        else:
            #pdb.set_trace()
            # FIXME: If a list is contained in a table cell or text box,
            # the list level must return to 1, even though the table or
            # textbox itself may be nested within another list.
            level = self.tagstack.count_tags(tag) + 1
            name = self.tagstack.rfindattr((TEXTNS, 'style-name'))
        self.writeout('</%s>\n' % self.listtypes.get(name))
        self.e_emptydata(tag)

    def s_text_list_item(self, tag, attrs):
        self.writeout('<li>')
        self.e_emptydata(tag, attrs)

    def e_text_list_item(self, tag, attrs):
        self.writedata()
        self.writeout('</li>\n')
        self.e_emptydata(tag)

    def s_text_list_level_style_bullet(self, tag, attrs):
        name = self.tagstack.stackparent()[(STYLENS, 'name')]
        self.listtypes[name] = 'ul'
        level = attrs[(TEXTNS, 'level')]
        self.currentstyle = ".%s_%s" % ( name.replace(".","_"), level)
        self.styledict[self.currentstyle] = {}

        level = int(level)
        if level % 3 == 1: listtype = "disc"
        if level % 3 == 2: listtype = "circle"
        if level % 3 == 0: listtype = "square"
        self.styledict[self.currentstyle]['list-style-type'] = listtype

    def e_text_list_level_style_bullet(self, tag, attrs):
        self.currentstyle = None

    def s_text_list_level_style_number(self, tag, attrs):
        name = self.tagstack.stackparent()[(STYLENS, 'name')]
        self.listtypes[name] = 'ol'
        level = attrs[(TEXTNS, 'level')]
        num_format = attrs.get((STYLENS, 'name'),"1")
        self.currentstyle = ".%s_%s" % ( name.replace(".","_"), level)
        self.styledict[self.currentstyle] = {}
        if   num_format == "1": listtype = "decimal"
        elif num_format == "I": listtype = "upper-roman"
        elif num_format == "i": listtype = "lower-roman"
        elif num_format == "A": listtype = "upper-alpha"
        elif num_format == "a": listtype = "lower-alpha"
        else: listtype = "decimal"
        self.styledict[self.currentstyle]['list-style-type'] = listtype

    def e_text_list_level_style_number(self, tag, attrs):
        self.currentstyle = None

    def s_text_note(self, tag, attrs):
        self.currentnote = self.currentnote + 1
        self.notedict[self.currentnote] = {}
        self.notebody = []

    def e_text_note(self, tag, attrs):
        pass

    def collectnote(self,s):
        if s != '':
            self.notebody.append(s)

    def s_text_note_body(self, tag, attrs):
        self.orgwfunc = self.wfunc
        self.wfunc = self.collectnote

    def e_text_note_body(self, tag, attrs):
        self.wfunc = self.orgwfunc
        self.notedict[self.currentnote]['body'] = ''.join(self.notebody)
        self.notebody = ''
        del self.orgwfunc

    def e_text_note_citation(self, tag, attrs):
        mark = ''.join(self.data)
        self.notedict[self.currentnote]['citation'] = mark
        self.writeout('<a href="#footnote-%s"><sup>%s</sup></a>' % (self.currentnote, mark))

    def s_text_p(self, tag, attrs):
        c = attrs.get((TEXTNS, 'style-name'), None)
        if c:
            self.writeout('<p class="P-%s">' % self.classname(attrs))
        else:
            self.writeout('<p>')
        self.e_emptydata(tag, attrs)

    def e_text_p(self, tag, attrs):
        self.writedata()
        self.writeout('</p>\n')
        self.e_emptydata(tag)

    def s_text_s(self, tag, attrs):
        c = attrs.get((TEXTNS, 'c'),"1")
        for x in xrange(int(c)):
            self.writeout('&nbsp;')

    def s_text_span(self, tag, attrs):
        self.writedata()
        self.writeout('<span class="S-%s">' % self.classname(attrs))
        self.e_emptydata(tag)

    def e_text_span(self, tag, attrs):
        self.writedata()
        self.writeout('</span>')
        self.e_emptydata(tag)

    def s_text_tab(self, tag, attrs):
        self.writedata()
        self.writeout(' ')
        self.e_emptydata(tag)

    def s_text_x_source(self, tag, attrs):
        self.writedata()
        self.e_emptydata(tag, attrs)
        self.s_ignorexml(tag, attrs)

    def e_text_x_source(self, tag, attrs):
        self.writedata()
        self.e_emptydata(tag)


#-----------------------------------------------------------------------------
#
# Reading the file
#
#-----------------------------------------------------------------------------

def odf2xhtml(odtfile):
    z = zipfile.ZipFile(odtfile)
    meta = z.read('meta.xml')
    content = z.read('content.xml')
    styles = z.read('styles.xml')
    z.close()

    odhandler = ODFContentHandler()
    # meta.xml
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(odhandler)
    parser.setErrorHandler(handler.ErrorHandler())

    inpsrc = InputSource()
    inpsrc.setByteStream(StringIO(meta))
    parser.parse(inpsrc)

    # styles.xml
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(odhandler)
    parser.setErrorHandler(handler.ErrorHandler())

    inpsrc = InputSource()
    inpsrc.setByteStream(StringIO(styles))
    parser.parse(inpsrc)

    # content.xml
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(odhandler)
    parser.setErrorHandler(handler.ErrorHandler())

    inpsrc = InputSource()
    inpsrc.setByteStream(StringIO(content))
    parser.parse(inpsrc)
    return odhandler.getxhtml()

#-------------------- ODFPARSER END

from email.MIMEMultipart import MIMEMultipart
from email.MIMENonMultipart import MIMENonMultipart
from email.MIMEText import MIMEText
from email import Encoders

def saveodtfile(odtstream):
    """ Save the ODT file"""
    tempfile = "/var/tmp/tempzip"
    f = open(tempfile,'w')
    f.write(odtstream.read())
    f.close()
    return tempfile


suffices = {
 'wmf':('image','x-wmf'),
 'png':('image','png'),
 'gif':('image','gif'),
 'jpg':('image','jpeg'),
 'jpeg':('image','jpeg')
 }

def odf2mht(self,odtfile):
    tmpfile = saveodtfile(odtfile)
    self.REQUEST.RESPONSE.setHeader('Content-Type','message/rfc822')
    msg = MIMEMultipart('related',type="text/html")
    msg.preamble = 'This is a multi-part message in MIME format.'
    msg.epilogue = ''
    result = odf2xhtml(tmpfile).encode('us-ascii','xmlcharrefreplace')
    htmlpart = MIMEText(result,'html','us-ascii')
    htmlpart['Content-Location'] = 'index.html'
    msg.attach(htmlpart)
    z = zipfile.ZipFile(tmpfile)
    for file in z.namelist():
        if file[0:9] == 'Pictures/':
            suffix = file[file.rfind(".")+1:]
            main,sub = suffices.get(suffix,('application','octet-stream')) 
            img = MIMENonMultipart(main,sub)
            img.set_payload(z.read(file))
            img['Content-Location'] = "" + file
            Encoders.encode_base64(img)
            msg.attach(img)
    z.close()
    unlink(tmpfile)
    return msg.as_string()
