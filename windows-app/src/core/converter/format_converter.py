import os
from pathlib import Path
from typing import Optional, Callable
import fitz
import docx

class FormatConverter:
    """Document Format Conversion Engine."""

    SUPPORTED_CONVERSIONS = {
        (".docx", ".pdf"),
        (".docx", ".txt"),
        (".pdf", ".txt"),
        (".pdf", ".docx"),
        (".txt", ".docx"),
        (".txt", ".pdf"),
        (".md", ".txt"),
        (".md", ".docx"),
    }

    @classmethod
    def can_convert(cls, src_ext: str, tgt_ext: str) -> bool:
        src_ext = src_ext.lower()
        tgt_ext = tgt_ext.lower()
        if src_ext == tgt_ext:
            return True
        return (src_ext, tgt_ext) in cls.SUPPORTED_CONVERSIONS

    @classmethod
    def convert(
        cls,
        src_path: str,
        tgt_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> bool:
        src_ext = Path(src_path).suffix.lower()
        tgt_ext = Path(tgt_path).suffix.lower()

        if src_ext == tgt_ext:
            import shutil
            shutil.copy2(src_path, tgt_path)
            return True

        if progress_callback:
            progress_callback(0.2, f"Converting {src_ext} to {tgt_ext}...")

        # PDF -> TXT
        if src_ext == ".pdf" and tgt_ext == ".txt":
            with fitz.open(src_path) as doc, open(tgt_path, "w", encoding="utf-8") as out:
                for page in doc:
                    out.write(page.get_text() + "\n")
            if progress_callback:
                progress_callback(1.0, "Conversion complete!")
            return True

        # DOCX -> TXT
        if src_ext == ".docx" and tgt_ext == ".txt":
            doc = docx.Document(src_path)
            with open(tgt_path, "w", encoding="utf-8") as out:
                for p in doc.paragraphs:
                    out.write(p.text + "\n")
            if progress_callback:
                progress_callback(1.0, "Conversion complete!")
            return True

        # TXT -> DOCX
        if src_ext in [".txt", ".md"] and tgt_ext == ".docx":
            doc = docx.Document()
            with open(src_path, "r", encoding="utf-8", errors="replace") as infile:
                for line in infile:
                    doc.add_paragraph(line.strip())
            doc.save(tgt_path)
            if progress_callback:
                progress_callback(1.0, "Conversion complete!")
            return True

        # PDF -> DOCX (Text flow extraction)
        if src_ext == ".pdf" and tgt_ext == ".docx":
            doc = fitz.open(src_path)
            out_doc = docx.Document()
            for page in doc:
                text = page.get_text()
                if text.strip():
                    for para in text.split("\n\n"):
                        if para.strip():
                            out_doc.add_paragraph(para.strip())
            out_doc.save(tgt_path)
            doc.close()
            if progress_callback:
                progress_callback(1.0, "Conversion complete!")
            return True

        # TXT -> PDF
        if src_ext in [".txt", ".md"] and tgt_ext == ".pdf":
            doc = fitz.open()
            page = doc.new_page()
            rect = fitz.Rect(50, 50, page.rect.width - 50, page.rect.height - 50)
            with open(src_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            page.insert_textbox(rect, content, fontsize=10, fontname="helv")
            doc.save(tgt_path, deflate=True)
            doc.close()
            if progress_callback:
                progress_callback(1.0, "Conversion complete!")
            return True

        raise NotImplementedError(f"Conversion from {src_ext} to {tgt_ext} is not supported directly.")

