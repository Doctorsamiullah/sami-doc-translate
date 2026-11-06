from typing import Optional, Callable
from src.core.parsers.base_parser import BaseDocumentParser

class TextParser(BaseDocumentParser):
    def get_total_units(self, file_path: str) -> int:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return max(1, sum(1 for _ in f))

    def translate_document(
        self,
        input_path: str,
        output_path: str,
        engine,
        src_lang: str = "en",
        tgt_lang: str = "hi",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        total_lines = self.get_total_units(input_path)
        current_line = 0

        with open(input_path, "r", encoding="utf-8", errors="replace") as infile, \
             open(output_path, "w", encoding="utf-8") as outfile:
            for line in infile:
                current_line += 1
                if line.strip():
                    translated = engine.translate(line.strip(), src_lang, tgt_lang)
                    outfile.write(translated + "\n")
                else:
                    outfile.write("\n")

                if progress_callback and current_line % 20 == 0:
                    progress_callback(current_line, total_lines, f"Processing line {current_line} of {total_lines}")

        if progress_callback:
            progress_callback(total_lines, total_lines, "Translation complete!")
        return True

