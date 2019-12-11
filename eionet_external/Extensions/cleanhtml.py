from __future__ import absolute_import
from mx.Tidy import *
import string

def cleanhtml(self, input, encoding='utf8'):
    full_html = 1
    if string.find(input, "<dtml-") >= 0:
       return (1, 0, input, 'Error: <dtml-... constructions are not allowed')
    if string.find(input.lower(),"<body") == -1:
       full_html = 0
    result = tidy(input,
#                 indent='auto',
                  word_2000=1,
                  clean=0,
                  output_xhtml=1,
                  output_errors=1,
                  output_markup=1,
                  drop_font_tags=1,
                  char_encoding=encoding,
                  )
    if full_html == 0:
       body = string.find(result[2],'<body')
       result = ( result[0], result[1], result[2][body+6:-17], result[3] )
    return result

def cleandisplay(self, input, encoding='utf8'):
    result = tidy(input,
#                 indent='auto',
                  word_2000=1,
                  clean=0,
                  output_xhtml=1,
                  output_errors=0,
                  output_markup=1,
                  drop_font_tags=1,
                  char_encoding=encoding,
                  )
    return result[2]
