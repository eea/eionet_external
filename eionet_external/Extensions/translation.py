#!/usr/local/bin/python
# -*- coding: utf-8
from __future__ import absolute_import
import sqlite, md5

import trans_threading
import six

lang_arg = 'lang'

# Threads: pool_sema is not a global variable, unless you import methods that use it
#pool_sema = threading.BoundedSemaphore()


def opendb():
    return sqlite.connect("translations.db", encoding="utf-8")

def savetext(transunitid, source):
    cx = opendb()
    cu = cx.cursor()
    cu.execute("INSERT INTO needtranslations VALUES (%s,'en',%s,1, NULL, '', 0)", transunitid, source)
    cx.commit()

def printtext(transunitid, source):
    f = open('trans','a')
    f.write("""INSERT INTO translations VALUES ('%s','en', '%s',1, NULL, '', 0);\n""" \
        % (transunitid, source.replace("'","\\'").encode('utf-8')))
    f.close()
    
def gettext(self, source):
    if type(source) == type(u''):
        source1byte = source#.encode('utf-8')
    else:
        source1byte = source
        source = six.text_type(source,'utf-8')
    transunitid = md5.new(source1byte).hexdigest()
    if source == '':
        return source#.encode('utf-8')
    if lang_arg not in self.REQUEST:
        return source#.encode('utf-8')
    langcode = self.REQUEST[lang_arg]
    cx = opendb()
    cu = cx.cursor()
    cu.execute("SELECT translation from translations WHERE transunitid=%s AND (langcode=%s OR issource=1) ORDER BY issource, fuzzy DESC", transunitid, langcode)
    row = cu.fetchone()
    if row == None:
        result = source
        printtext(transunitid, source)
    else:
        result = row.translation
    cx.close()
    return result#.encode('utf-8')

# Unused
def gettext_write(self, source):
    if type(source) == type(u''):
        source1byte = source#.encode('utf-8')
    else:
        source1byte = source
        source = six.text_type(source,'utf-8')
    transunitid = md5.new(source1byte).hexdigest()
    if source == '':
        return source
    if lang_arg not in self.REQUEST:
        return source
    langcode = self.REQUEST[lang_arg]
    if not trans_threading.acquire(): # Check with no wait
        result = source
    else:
        cx = opendb()
        cu = cx.cursor()
        cu.execute("SELECT translation from translations WHERE transunitid=%s AND (langcode=%s OR issource=1) ORDER BY issource, fuzzy DESC", transunitid, langcode)
        cx.commit()
        row = cu.fetchone()
        if row == None:
            cu.execute("INSERT INTO translations VALUES (%s,'en',%s,1, NULL, '', 0)", transunitid, source)
            cx.commit()
            result = source
        else:
            result = row.translation
    cx.close()
    trans_threading.release()
    return result

#cu.execute("INSERT INTO translations VALUES ('aabbccddeeffgghh','en',%s,1, NULL, '',0)", u"Hello iæblegrød")
#cx.commit()

if __name__ == '__main__':
    """ """
#   print gettext(u"Welcome", {'langcode':'da'})

# vim: set expandtab sw=4 ai :
