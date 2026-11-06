from abc import ABC, abstractmethod
from typing import Generator, Any, Callable, Optional

class BaseDocumentParser(ABC):
    """
    Abstract streaming document parser.
    Ensures documents of unlimited size are processed page-by-page or block-by-block.
    """
    @abstractmethod
    def get_total_units(self, file_path: str) -> int:
        """Returns total number of pages or sections in document."""
        pass

    @abstractmethod
    def translate_document(
        self,
        input_path: str,
        output_path: str,
        engine: Any,
        src_lang: str = "en",
        tgt_lang: str = "hi",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        """
        Processes and streams translated content to disk without loading
        the full document into RAM.
        """
        pass

