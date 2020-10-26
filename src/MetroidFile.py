import gciso

class MetroidFile(gciso.IsoFile):
    def __init__(self, isoPath):
        super().__init__(isoPath)
        self.selected_file = None
        self.fileOffset = None

    def _readFile(self, fileOffset, fileSize, offset=0, count=-1):
        data = super()._readFile(fileOffset, fileSize, offset=0, count=-1)
        self.file.seek(fileOffset + offset)
        return data

    def seekFile(self, path, offset=0, count=-1):
        MetroidFile._checkPath(path)
        fileOffset, fileSize = self.files[path]
        self.fileOffset = fileOffset
        self._readFile(fileOffset, fileSize, offset, count)

    def selectFile(self, path):
        if isinstance(path, str):
            path = path.encode()
        MetroidFile._checkPath(path)
        fileOffset, fileSize = self.files[path]
        self.file.seek(fileOffset)
        self.selected_file = self.file.read(fileSize)

    def readBytes(self, count):
        return self.file.read(count)

    def writeBytes(self, data):
        if isinstance(data, str):
            data = data.encode()
        self.file.write(data)