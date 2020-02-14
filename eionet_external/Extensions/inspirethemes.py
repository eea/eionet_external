#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Søren Roug, European Environment Agency
#
from __future__ import absolute_import
from __future__ import print_function
import _mysql

dbhost = "penguin"
dbdb = "inspirethemes"
dbuser = "itread"
dbpass = "readit"

cachedresult = None

def list_all(self, REQUEST=None, RESPONSE=None):
    global cachedresult
    if cachedresult != None: return cachedresult
    cachedresult = []
    db = _mysql.connect(host=dbhost,user=dbuser, passwd=dbpass, db=dbdb,
       connect_timeout = 30)
#   db.set_character_set("utf8")
    db.query("SELECT id_inspire_theme, name, langcode, definition FROM inspire_theme ORDER BY langcode, id_inspire_theme")
    r = db.store_result()
    return r.fetch_row(maxrows=0)
    while (1):
        row = r.fetch_row(maxrows=0)
        if row == None:
            break
        cachedresult.append({'id_inspire_theme': row[0],
           'name': row[1], 'langcode':row[2],
           'definition':row[3]})
    cursor.close()
    db.close()
    return cachedresult

if __name__ == '__main__':
    res = list_all(None)
    for item in res:
        print(item[1])



# vim: set expandtab sw=4 ai :

