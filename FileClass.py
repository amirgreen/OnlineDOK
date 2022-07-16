import os

class FileClass:

    #size
    def __init__(self, name, path):
        self.name = name
        self.path = path
        size = os.path.getsize(unicode(self.path) + '/' + unicode(self.name))
        self.size = str(size) + 'B'
        if size > 1000:
            self.size = str(size/1000) + 'KB'
        if size > 1000000:
            self.size = str(size/1000000) + 'MB'
        if size > 1000000000000:
            self.size = str(size/1000000000000) + 'GB'

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def __repr__(self):
        return self.name