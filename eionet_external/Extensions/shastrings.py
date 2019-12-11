
import sha

def sha1(self, s):
    if s is None:
        return ''
    return sha.new(str(s)).hexdigest()
