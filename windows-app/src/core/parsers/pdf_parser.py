import fitz  # PyMuPDF
from typing import Optional, Callable
from src.core.parsers.base_parser import BaseDocumentParser
from src.core.fonts.font_manager import FontManager

class PdfParser(BaseDocumentParser):
    def get_total_units(self, file_path: str) -> int:
        with fitz.open(file_path) as doc:
            return len(doc)

    def translate_document(
        self,
        input_path: str,
        output_path: str,
        engine,
        src_lang: str = "en",
        tgt_lang: str = "hi",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        doc = fitz.open(input_path)
        total_pages = len(doc)

        try:
            for page_num in range(total_pages):
                page = doc[page_num]
                blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no, block_type)

                for b in blocks:
                    if b[6] == 0:  # Text block
                        orig_text = b[4].strip()
                        if orig_text:
                            translated_text = engine.translate(orig_text, src_lang, tgt_lang)
                            rect = fitz.Rect(b[0], b[1], b[2], b[3])
                            
                            # Cleanly redact existing text block
                            page.add_redact_annot(rect, fill=(1, 1, 1))
                            page.apply_redactions()

                            # Font scaling calculation
                            scale = FontManager.calculate_hindi_scale_factor(len(orig_text), len(translated_text))
                            fontsize = max(8.0, 11.0 * scale)

                            # Re-insert translated text
                            page.insert_textbox(
                                rect,
                                translated_text,
                                fontsize=fontsize,
                                fontname="helv" if tgt_lang == "en" else "hebi",
                                color=(0, 0, 0),
                                align=fitz.TEXT_ALIGN_LEFT
                            )

                if progress_callback:
                    progress_callback(page_num + 1, total_pages, f"Translated page {page_num + 1} of {total_pages}")

            # Save with maximum deflating and garbage collection
            doc.save(output_path, deflate=True, garbage=4)
            return True
        finally:
            doc.close()

