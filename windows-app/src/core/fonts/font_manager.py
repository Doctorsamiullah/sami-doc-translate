from typing import Dict, List

class FontManager:
    """
    Manages Devanagari typography, font families, and categories.
    Supports Modern Clean (Google Fonts/Unicode) and Traditional / Government fonts.
    """

    MODERN_FONTS = [
        "Noto Sans Devanagari",
        "Hind",
        "Mukta",
        "Poppins",
        "Yantramanav"
    ]

    TRADITIONAL_FONTS = [
        "Mangal",
        "Kruti Dev 010",
        "Tiro Devanagari Hindi",
        "Martel",
        "Karma",
        "Aparajita"
    ]

    ALL_FONTS = MODERN_FONTS + TRADITIONAL_FONTS

    FONT_DESCRIPTIONS: Dict[str, str] = {
        "Noto Sans Devanagari": "Highly legible, universally compatible, Google Unicode standard.",
        "Hind": "Monolinear, punchy sans-serif optimized for modern UI and mobile reading.",
        "Mukta": "Compact, humanist sans-serif designed to fit long text cleanly in tight spaces.",
        "Poppins": "Geometric, highly aesthetic font ideal for tech platforms & clean bilingual layouts.",
        "Yantramanav": "Industrial-feeling sans-serif with high structural stability for clean headlines.",
        "Mangal": "The baseline Unicode standard used across government portals and official exams.",
        "Kruti Dev 010": "Premier typewriter layout standard for physical publishing and legal printing presses.",
        "Tiro Devanagari Hindi": "Scholarly serif font styled after classic 19th-century metal prints.",
        "Martel": "High-contrast serif tailored for newspapers, legal blogs, and editorial publications.",
        "Karma": "Elegant reading serif optimized to feel soft on low-resolution displays.",
        "Aparajita": "Thin digital Unicode option widely preferred for formal government documentation."
    }

    @classmethod
    def get_all_font_names(cls) -> List[str]:
        return cls.ALL_FONTS

    @classmethod
    def get_default_font(cls) -> str:
        return "Noto Sans Devanagari"

    @classmethod
    def calculate_hindi_scale_factor(cls, orig_len: int, translated_len: int) -> float:
        if orig_len <= 0 or translated_len <= 0:
            return 1.0
        ratio = translated_len / orig_len
        if ratio > 1.15:
            return max(0.75, 1.0 / (ratio * 0.95))
        return 1.0
