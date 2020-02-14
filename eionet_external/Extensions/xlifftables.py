# -*- coding: UTF-8 -*-
#
# NOTE:
# This parser doesn't understand the ALT-TRANS element.

from __future__ import absolute_import
from __future__ import print_function
from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO
from types import StringType, UnicodeType
from cgi import escape

#constants
_FILE_ATTRS = ['original', 'source-language', 'datatype', 'date',
          'target-language', 'product-name', 'product-version', 'build-num']
_PHASE_ATTRS = ['phase-name', 'process-name', 'tool', 'date', 'contact-name',
          'contact-email', 'company-name']


class XLIFFHandler(ContentHandler):
    """ This is used to parse the xliff file
    """

    def __init__(self):
        """constructor """
        self.__currentTag = ''
        self.__phase_group = []
        self.__source = 0
        self.__data = []
        self.__inside_alttrans = 0
        self.__tuid = ''
        self._toprint = []

    def toprint(self, s):
        self._toprint.append(s)

    def getResult(self):
        return '\n'.join(self._toprint)

    #functions related with <phase-group> tag
    def getPhaseGroup(self):
        return self.__phase_group

    def setPhaseGroup(self, dict):
        self.__phase_group.append(dict)

    def startElement(self, name, attrs):
        self.__currentTag = name

        if name == 'alt-trans':
            self.__inside_alttrans = 1
        # Make the attributes available
        # Implicit assumption: There is only one <file> element.
        if name == 'file':
            self.toprint('<p style="border: 1px solid black; background-color:#f0f0f0;">')
            self.toprint('File name: %s<br/>' % attrs.get('original',''))
            self.toprint('Source language: %s - Target language: %s<br/>' % (attrs.get('source-language','Unknown'), attrs.get('target-language','Unknown')))
            self.toprint('</p>')
            self.toprint('<table class="datatable">')
            self.toprint('<col style="width:7%"/>')
            self.toprint('<col style="width:31%"/>')
            self.toprint('<col style="width:31%"/>')
            self.toprint('<col style="width:31%"/>')
            self.toprint("""<tr><th>Id</th><th>Source</th><th>Target</th><th>Note</th></tr>""")

        if name == 'phase':
            tmp = list(attrs.items())
            for i in [elem for elem in attrs.keys() if elem not in _PHASE_ATTRS]:
                tmp.remove((i, attrs[i]))
            self.setPhaseGroup(tmp)

        if name == 'trans-unit':
            self.toprint('<tr>')
            self.__tuid = attrs['id']
            self.__source = u''
            self.__target = u''
            self.__note = u''

    def endElement(self, name):
        if name == 'alt-trans':
            self.__inside_alttrans = 0

        if name == 'file':
            self.toprint('</table>')

        if name == 'source' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__source = content

        if name == 'target' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__target = content

        if name == 'note' and self.__inside_alttrans == 0:
            content = u''.join(self.__data).strip()
            self.__data = []
            self.__note = content

        if name == 'trans-unit':
            self.toprint('<td>%s</td>' % escape(self.__tuid))
            self.toprint('<td>%s</td>' % escape(self.__source))
            self.toprint('<td>%s</td>' % escape(self.__target))
            self.toprint('<td>%s</td>' % escape(self.__note))
            self.toprint('</tr>')

        self.__currentTag = ''

    def characters(self, content):
        currentTag = self.__currentTag
        if currentTag in ( 'source', 'target', 'note'):
            self.__data.append(content)

class HandleXliffParsing:
    """ class for parse xliff files """

    def __init__(self):
        """ """
        pass

    def parseXLIFFSTring(self, xml_string):
        """ """
        chandler = XLIFFHandler()
        parser = make_parser()
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)
        # Don't load the DTD from the Internet
        parser.setFeature(handler.feature_external_ges, 0)
        inpsrc = InputSource()
        inpsrc.setByteStream(StringIO(xml_string))
        try:
            parser.parse(inpsrc)
            return chandler
        except:
            return None

    def parseXLIFFFile(self, file):
        # Create a parser
        parser = make_parser()
        chandler = XLIFFHandler()
        # Tell the parser to use our handler
        parser.setContentHandler(chandler)
        # Don't load the DTD from the Internet
        parser.setFeature(handler.feature_external_ges, 0)
        inputsrc = InputSource()

        try:
            if type(file) is StringType:
                inputsrc.setByteStream(StringIO(file))
            else:
                filecontent = file.read()
                inputsrc.setByteStream(StringIO(filecontent))
            parser.parse(inputsrc)
            return chandler
        except:
            return None


def xliff2tables(content):
    parser = HandleXliffParsing()
    chandler = parser.parseXLIFFFile(content)
    if chandler is None:
        return ("Unable to parse XLIFF file")

    return chandler.getResult()

if __name__ == '__main__':
    xliff = open('global.xlf').read()
    print(xliff2html(xliff))
