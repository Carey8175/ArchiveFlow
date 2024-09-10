
class URL:
    def __init__(
            self,
            url: str,
            exclude_dirs: Optional[str] = None,
            max_depth: int = -1
    ) -> None:

        self.url = url
        self.exclude_dirs = exclude_dirs
        self.max_depth = max_depth