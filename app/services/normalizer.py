import re
import unicodedata

ARABIC_TO_PERSIAN = str.maketrans(
    {
        "ي": "ی",
        "ى": "ی",
        "ئ": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "هٔ",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "ٱ": "ا",
    }
)

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "۰۱۲۳۴۵۶۷۸۹")
LATIN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
DIACRITICS = re.compile(r"[\u064b-\u065f\u0670\u06d6-\u06ed]")
SPACE_BEFORE_PUNCTUATION = re.compile(r"\s+([،؛؟!٪»)\]}.])")
SPACE_AFTER_PUNCTUATION = re.compile(r"([،؛؟!])(?=[^\s»)\]}.])")
MULTIPLE_SPACES = re.compile(r"[ \t]+")
MULTIPLE_BLANK_LINES = re.compile(r"\n{3,}")

ZWNJ_PREFIXES = (
    "می",
    "نمی",
)
ZWNJ_SUFFIXES = (
    "ها",
    "های",
    "هایی",
    "تر",
    "ترین",
)


def normalize_persian(text: str, convert_latin_digits: bool = False) -> str:
    """Normalize character variants and spacing without changing the meaning."""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(ARABIC_TO_PERSIAN).translate(ARABIC_DIGITS)
    if convert_latin_digits:
        text = text.translate(LATIN_DIGITS)
    text = DIACRITICS.sub("", text)
    text = text.replace("\u200f", "").replace("\u200e", "")
    text = re.sub(r"\b(ن?می)\s+([\u0600-\u06ff]+)", r"\1‌\2", text)
    text = re.sub(
        r"([\u0600-\u06ff]+)\s+(ها(?:یی?|یم|یت|یش|مان|تان|شان)?|تر(?:ین)?)\b",
        r"\1‌\2",
        text,
    )
    text = SPACE_BEFORE_PUNCTUATION.sub(r"\1", text)
    text = SPACE_AFTER_PUNCTUATION.sub(r"\1 ", text)
    text = MULTIPLE_SPACES.sub(" ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = MULTIPLE_BLANK_LINES.sub("\n\n", text)
    return text.strip()


def ensure_punctuation(text: str) -> str:
    text = text.strip()
    if text and text[-1] not in ".!؟?…":
        text += "."
    return text

