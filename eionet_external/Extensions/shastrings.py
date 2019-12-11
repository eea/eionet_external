
from __future__ import absolute_import
import hashlib

def sha1(self, s):
    if s is None:
        return ''
    return hashlib.new(str(s)).hexdigest()
