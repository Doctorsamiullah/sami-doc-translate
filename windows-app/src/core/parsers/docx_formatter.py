import re
import docx
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from typing import Optional, Callable

class DocxStyleFormatter:
    """
    Applies custom typography hierarchy, heading/subheading styles,
    and automatic numbering schemes to DOCX documents.
    """

    DEVANAGARI_DIGITS = {
        '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
        '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
    }

    @classmethod
    def to_devanagari_num(cls, num: int) -> str:
        return "".join(cls.DEVANAGARI_DIGITS.get(d, d) for d in str(num))

    @classmethod
    def apply_devanagari_font(cls, run, font_name: str):
        run.font.name = font_name
        rPr = run._r.get_or_add_rPr()
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rPr.append(rFonts)
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:cs'), font_name)

    @classmethod
    def format_document(
        cls,
        input_path: str,
        output_path: str,
        font_name: str = "Noto Sans Devanagari",
        heading1_size: int = 16,
        subheading_size: int = 13,
        body_size: int = 11,
        numbering_style: str = "1.1, 1.2 (Arabic)",
        apply_bold_headings: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        doc = docx.Document(input_path)
        total_p = len(doc.paragraphs)

        h1_counter = 0
        h2_counter = 0

        heading_pattern = re.compile(r'^(stage|chapter|section|part|चरण|अध्याय|धारा|भाग)\s*\d+[:\s]', re.IGNORECASE)
        subheading_pattern = re.compile(r'^[a-z0-9]+[\.\)]\s*', re.IGNORECASE)

        for i, p in enumerate(doc.paragraphs):
            text = p.text.strip()
            if not text:
                continue

            is_h1 = (p.style.name.startswith("Heading 1") or 
                     bool(heading_pattern.match(text)) or 
                     (text.isupper() and len(text) < 80))
            is_h2 = (p.style.name.startswith("Heading 2") or 
                     p.style.name.startswith("Heading 3") or 
                     bool(subheading_pattern.match(text)))

            if is_h1:
                h1_counter += 1
                h2_counter = 0
                # Format Heading 1
                for run in p.runs:
                    run.font.size = Pt(heading1_size)
                    run.bold = apply_bold_headings
                    cls.apply_devanagari_font(run, font_name)
            elif is_h2:
                h2_counter += 1
                # Format Subheading with numbering
                prefix = ""
                if numbering_style.startswith("1.1"):
                    prefix = f"{max(1, h1_counter)}.{h2_counter} "
                elif numbering_style.startswith("१.१"):
                    prefix = f"{cls.to_devanagari_num(max(1, h1_counter))}.{cls.to_devanagari_num(h2_counter)} "
                elif numbering_style.startswith("A."):
                    prefix = f"{chr(64 + min(26, h2_counter))}. "
                elif numbering_style.startswith("a."):
                    prefix = f"{chr(96 + min(26, h2_counter))}. "

                # Strip existing manual numbering if we are applying auto numbering
                cleaned_text = subheading_pattern.sub("", text)
                if prefix and not text.startswith(prefix):
                    if p.runs:
                        p.runs[0].text = prefix + cleaned_text
                        for r in p.runs[1:]:
                            r.text = ""

                for run in p.runs:
                    run.font.size = Pt(subheading_size)
                    run.bold = True
                    cls.apply_devanagari_font(run, font_name)
            else:
                # Regular body text
                for run in p.runs:
                    run.font.size = Pt(body_size)
                    cls.apply_devanagari_font(run, font_name)

            if progress_callback and (i + 1) % 10 == 0:
                progress_callback(i + 1, total_p, f"Formatting paragraph {i+1} of {total_p}")

        # Also format tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.size = Pt(body_size)
                            cls.apply_devanagari_font(run, font_name)

        doc.save(output_path)
        if progress_callback:
            progress_callback(total_p, total_p, "Styling applied successfully!")
        return True

