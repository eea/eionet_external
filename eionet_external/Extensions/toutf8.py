
def UnicodeEntities(self,str,charset):
    strlist = list(str)
    res = ""
    if (charset == 'iso-8859-7'):
        for ch in strlist:
            if(ord(ch) >= 0xb4):
                res = res + "&#" + repr(ord(ch) + 720) + ";"
            else:
                res = res + ch

    elif (charset == 'iso-8859-5'):
        for ch in strlist:
            if(ord(ch) >= 0xa0):
                res = res + "&#" + repr(ord(ch) + 864) + ";"
            else:
                res = res + ch

    elif charset == 'utf-8':
        res = str.decode('utf-8')

    else:                #Assume iso-8859-1 if unknown charset
        for ch in strlist:
            if(ord(ch) >= 0x96):
                res = res + "&#" + repr(ord(ch)) + ";"
            else:
                res = res + ch
    return res
