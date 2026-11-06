import docx
from docx.shared import Pt, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from typing import Optional, Callable
from src.core.parsers.base_parser import BaseDocumentParser
from src.core.fonts.font_manager import FontManager

class DocxParser(BaseDocumentParser):
    def get_total_units(self, file_path: str) -> int:
        doc = docx.Document(file_path)
        total_p = len(doc.paragraphs)
        for table in doc.tables:
            for row in table.rows:
                total_p += len(row.cells)
        return max(1, total_p)

    def _apply_devanagari_font(self, run, font_name: str = "Noto Sans Devanagari"):
        run.font.name = font_name
        rPr = run._r.get_or_add_rPr()
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rPr.append(rFonts)
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:cs'), font_name)

    def translate_document(
        self,
        input_path: str,
        output_path: str,
        engine,
        src_lang: str = "en",
        tgt_lang: str = "hi",
        font_name: str = "Noto Sans Devanagari",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        doc = docx.Document(input_path)
        total_units = self.get_total_units(input_path)
        current_unit = 0

        # Translate body paragraphs as complete semantic sentences
        for p in doc.paragraphs:
            raw_text = p.text.strip()
            if raw_text:
                translated_text = engine.translate(raw_text, src_lang, tgt_lang)
                if p.runs:
                    p.runs[0].text = translated_text
                    if tgt_lang == "hi":
                        self._apply_devanagari_font(p.runs[0], font_name)
                    for r in p.runs[1:]:
                        r.text = ""
                else:
                    new_run = p.add_run(translated_text)
                    if tgt_lang == "hi":
                        self._apply_devanagari_font(new_run, font_name)

            current_unit += 1
            if progress_callback and current_unit % 5 == 0:
                progress_callback(current_unit, total_units, f"Processing paragraph {current_unit} of {total_units}")

        # Translate tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        translated_cell = engine.translate(cell_text, src_lang, tgt_lang)
                        if cell.paragraphs and cell.paragraphs[0].runs:
                            cell.paragraphs[0].runs[0].text = translated_cell
                            if tgt_lang == "hi":
                                self._apply_devanagari_font(cell.paragraphs[0].runs[0], font_name)
                            for r in cell.paragraphs[0].runs[1:]:
                                r.text = ""
                            for p_extra in cell.paragraphs[1:]:
                                for r in p_extra.runs:
                                    r.text = ""
                        else:
                            p = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()
                            new_run = p.add_run(translated_cell)
                            if tgt_lang == "hi":
                                self._apply_devanagari_font(new_run, font_name)

                    current_unit += 1
                    if progress_callback and current_unit % 5 == 0:
                        progress_callback(current_unit, total_units, f"Processing table cell {current_unit} of {total_units}")

        try:
            doc.save(output_path)
        except PermissionError:
            from pathlib import Path
            p = Path(output_path)
            alt_path = str(p.with_name(f"{p.stem}_translated{p.suffix}"))
            doc.save(alt_path)

        if progress_callback:
            progress_callback(total_units, total_units, "Translation complete!")
        return True
