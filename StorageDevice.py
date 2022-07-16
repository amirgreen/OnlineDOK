from Partition import Partition


class StorageDevice:

    usbCount = 0
    def __init__(self, name, size, label, jsonPartitions):
        if name == 'mmcblk0':
            self.secondName = 'SD Card'
        else:
            self.secondName = 'USB ' + str(StorageDevice.usbCount)

        StorageDevice.usbCount += 1
        self.label = label
        self.name = name
        self.size = size
        self.partitions = []
        for p in jsonPartitions:
            self.partition = Partition(p['name'], p['mountpoint'], p['fstype'], p['size'])
            self.partitions.append(self.partition)



    def getName(self):
        return self.name

    def getPath(self):
        return self.type

    def getLabel(self):
        return self.label

    def getPartitions(self):
        return self.partitions

    def getSize(self):
        return self.size

    def __repr__(self):
        return "name: " + self.name