class Documento:
    def __init__(self, filename, content, checksum, metadata):
        self.filename = filename
        self.content = content
        self.checksum = checksum
        self.metadata = metadata
