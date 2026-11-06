from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Dict

class ITranslationEngine(ABC):
    @abstractmethod
    def translate(self, text: str, src: str, tgt: str) -> str:
        """Translates a single string between English and Hindi."""
        pass

    @abstractmethod
    def translate_batch(self, texts: List[str], src: str, tgt: str) -> List[str]:
        """Translates a batch of strings concurrently."""
        pass

    @abstractmethod
    def is_model_available(self, src: str, tgt: str) -> bool:
        """Checks if local neural weights are loaded."""
        pass

