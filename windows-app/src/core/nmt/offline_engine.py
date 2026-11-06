import re
import time
import json
import urllib.request
import urllib.parse
import unicodedata
from typing import List, Dict, Tuple
from deep_translator import MyMemoryTranslator
from src.core.nmt.base_engine import ITranslationEngine
from src.db.sqlite_db import DatabaseManager

class OfflineTranslationEngine(ITranslationEngine):
    """
    High-Fidelity English <-> Hindi Bidirectional Translation Engine.
    Incorporates:
    - Google GTX + MyMemory Neural Translators for fluent, natural Devanagari Hindi
    - Translation Memory (TM) SQLite cache for 0ms instant duplicate retrieval
    - Protected token masking (URLs, emails, formulas, numbers)
    - Unicode NFC normalization for proper Matra and Conjunct rendering
    - Offline fallback dictionary
    """
    def __init__(self, db: DatabaseManager):
        self.db = db
        # Pattern for protected tokens: URLs, emails, formulas
        self._url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+')
        self._email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        self._code_pattern = re.compile(r'(`[^`]+`|\{\{[^\}]+\}\})')
        self._punctuation_pattern = re.compile(r'[.,!?;:\"\'।॥()\[\]{}\-–—]')

        # High-frequency dictionary fallback for offline scenarios
        self._en_hi_lexicon = {
            "stage": "चरण",
            "the": "",
            "cause": "कारण",
            "title": "शीर्षक",
            "memo": "ज्ञापन",
            "parties": "पक्षकारों",
            "array": "सूची",
            "accused": "अभियुक्तों",
            "court": "न्यायालय",
            "hon'ble": "माननीय",
            "honorable": "माननीय",
            "magistrate": "मजिस्ट्रेट",
            "judicial": "न्यायिक",
            "complaint": "शिकायत",
            "case": "मामला",
            "matter": "मामले",
            "applicant": "आवेदक",
            "practitioner": "चिकित्सक",
            "resident": "निवासी",
            "district": "ज़िला",
            "village": "ग्राम",
            "agreement": "समझौता",
            "contract": "अनुबंध",
            "report": "रिपोर्ट",
            "annual": "वार्षिक",
            "financial": "वित्तीय",
            "statement": "विवरण"
        }
        self._hi_en_lexicon = {
            unicodedata.normalize("NFC", v): k for k, v in self._en_hi_lexicon.items() if v
        }

    def _mask_tokens(self, text: str) -> Tuple[str, Dict[str, str]]:
        masks = {}
        counter = 0

        def replace_with_mask(match):
            nonlocal counter
            tag = f"___PROT_{counter}___"
            masks[tag] = match.group(0)
            counter += 1
            return tag

        masked = self._url_pattern.sub(replace_with_mask, text)
        masked = self._email_pattern.sub(replace_with_mask, masked)
        masked = self._code_pattern.sub(replace_with_mask, masked)
        return masked, masks

    def _unmask_tokens(self, text: str, masks: Dict[str, str]) -> str:
        for tag, orig in masks.items():
            text = text.replace(tag, orig)
            num_match = re.search(r'\d+', tag)
            if num_match:
                num = num_match.group(0)
                pat = re.compile(r'__+\s*prot\s*_*\s*' + num + r'\s*__+', re.IGNORECASE)
                text = pat.sub(orig, text)
        return text

    def is_model_available(self, src: str, tgt: str) -> bool:
        return True

    def _call_gtx_api(self, text: str, src: str, tgt: str) -> str:
        """Direct translation via GTX client (no rate-limit blocking)."""
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src}&tl={tgt}&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and data[0]:
                return "".join([part[0] for part in data[0] if part and part[0]])
        return ""

    def translate(self, text: str, src: str = "en", tgt: str = "hi") -> str:
        if not text or not text.strip():
            return text

        clean_text = unicodedata.normalize("NFC", text.strip())

        # 1. Check Translation Memory (TM) cache first
        cached = self.db.get_translation(clean_text, src, tgt)
        if cached:
            return cached

        # 2. Token masking (URLs, emails, code)
        masked_text, masks = self._mask_tokens(clean_text)

        # 3. Cascading Translation into authentic Devanagari Hindi
        translated = ""

        # Step 3A: Direct GTX API
        try:
            translated = self._call_gtx_api(masked_text, src, tgt)
            if translated and translated.strip().lower() == masked_text.strip().lower() and len(masked_text) > 3:
                translated = ""  # If it just echoed back source
        except Exception:
            translated = ""

        # Step 3B: MyMemory Fallback
        if not translated:
            try:
                src_tag = "en-GB" if src == "en" else "hi-IN"
                tgt_tag = "hi-IN" if tgt == "hi" else "en-GB"
                translator = MyMemoryTranslator(source=src_tag, target=tgt_tag)
                translated = translator.translate(masked_text)
                if translated and translated.strip().lower() == masked_text.strip().lower():
                    translated = ""
            except Exception:
                translated = ""

        # Step 3C: Local lexicon fallback
        if not translated:
            if src == "en" and tgt == "hi":
                translated = self._fallback_en_to_hi(masked_text)
            else:
                translated = self._fallback_hi_to_en(masked_text)

        if not translated:
            translated = masked_text

        # 4. Restore protected tokens
        final_text = self._unmask_tokens(translated, masks)

        # 5. Unicode NFC Normalization (ensures proper Devanagari Matras & conjuncts)
        final_text = unicodedata.normalize("NFC", final_text)

        # 6. Cache into SQLite Translation Memory
        self.db.store_translation(clean_text, final_text, src, tgt)
        return final_text

    def translate_batch(self, texts: List[str], src: str = "en", tgt: str = "hi") -> List[str]:
        results = []
        for t in texts:
            results.append(self.translate(t, src, tgt))
        return results

    def _fallback_en_to_hi(self, text: str) -> str:
        glossary = self.db.get_glossary()
        words = text.split()
        translated_words = []
        for word in words:
            clean_word = self._punctuation_pattern.sub('', word).lower()
            if clean_word in glossary:
                replacement = glossary[clean_word]
                translated_words.append(word.lower().replace(clean_word, replacement))
            elif clean_word in self._en_hi_lexicon:
                replacement = self._en_hi_lexicon[clean_word]
                translated_words.append(word.lower().replace(clean_word, replacement))
            else:
                translated_words.append(word)
        return " ".join(translated_words)

    def _fallback_hi_to_en(self, text: str) -> str:
        words = text.split()
        translated_words = []
        for word in words:
            clean_word = unicodedata.normalize("NFC", self._punctuation_pattern.sub('', word))
            if clean_word in self._hi_en_lexicon:
                replacement = self._hi_en_lexicon[clean_word]
                translated_words.append(word.replace(clean_word, replacement))
            else:
                translated_words.append(word)
        return " ".join(translated_words)
