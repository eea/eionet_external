"""Convert html data to raw text"""

from __future__ import absolute_import
from sgmllib import SGMLParser
from string import join

# Code taken from Dieter Maurer's CatalogSupport Module
# http://www.handshake.de/~dieter/pyprojects/zope
# Thank you!

class _StripTagParser(SGMLParser):
  '''SGML Parser removing any tags and translating HTML entities.'''

  from six.moves.html_entities import entitydefs

  data= None

  def handle_data(self,data):
    if self.data is None: self.data=[]
    self.data.append(data)

  def __str__(self):
    if self.data is None: return ''
    return join(self.data,'')


def StripTags(data):
    """Convert html data to raw text"""

    p = _StripTagParser()

    try:
        p.feed(data)
        p.close()
        return str(p)
    except:
        return ''
