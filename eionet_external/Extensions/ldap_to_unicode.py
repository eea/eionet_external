def convert(self):
    try:
        return self.data[0].decode('utf-8')
    except AttributeError:
        return ""
