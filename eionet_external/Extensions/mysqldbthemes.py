#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Søren Roug, European Environment Agency
#
import MySQLdb

dbhost = "penguin"
dbdb = "inspirethemes"
dbuser = "itread"
dbpass = "readit"

cachedresult = None

def list_all(self, REQUEST=None, RESPONSE=None):
    global cachedresult
    if cachedresult != None: return cachedresult
    cachedresult = []
    db = MySQLdb.connect(dbhost,dbuser, dbpass, dbdb,
       connect_timeout = 30, use_unicode = True)
    cursor = db.cursor()
    cursor.execute ("SELECT id_inspire_theme, name, langcode, definition FROM inspire_theme ORDER BY langcode, id_inspire_theme")
    while (1):
        row = cursor.fetchone()
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
        print item['name'].encode('utf-8')



# vim: set expandtab sw=4 ai :

