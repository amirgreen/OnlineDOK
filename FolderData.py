import os
import unicodedata
from FileClass import FileClass


class FolderData:

    def __init__(self, path):
        self.path = path
        self.dirlist = []
        self.filelist = []
        for filename in os.listdir(path):
            if filename[0] != '.':
                if os.path.isdir(os.path.join(path, filename)):
                    self.dirlist.append(filename)
                if os.path.isfile(os.path.join(path, filename)):
                    self.filelist.append(FileClass(filename, path))

    def getPath(self):
        return self.path

    def filesInFolder(self):
        return self.filelist

    def dirsInFolder(self):
        return self.dirlist

    def __repr__(self):
        return "path: " + self.path


