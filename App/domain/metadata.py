class Metadata:
    def __init__(
        self,
        file_size: int,
        mime_type: str,
        page_count: int | None = None
    ):
        self.file_size = file_size
        self.mime_type = mime_type
        self.page_count = page_count
