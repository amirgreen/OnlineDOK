class Partition:

    def __init__(self, name, path, fs, size):
        self.name = name
        self.path = path
        self.fs = fs
        self.size = size


    def getName(self):
        return self.name

    def getPath(self):
        return self.type

    def getLabel(self):
        return self.label

    def getType(self):
        return self.type

    def getSize(self):
        return self.size

    def __repr__(self):
        return "path: " + self.path