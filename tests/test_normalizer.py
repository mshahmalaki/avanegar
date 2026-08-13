from avanegar.services.normalizer import ensure_punctuation, normalize_persian


def test_arabic_variants_are_normalized() -> None:
    assert normalize_persian("كتاب فارسي") == "کتاب فارسی"


def test_arabic_digits_are_converted_but_latin_digits_are_preserved() -> None:
    assert normalize_persian("نسخه 2 در سال ٢٠٢٦") == "نسخه 2 در سال ۲۰۲۶"


def test_common_prefixes_and_suffixes_use_zwnj() -> None:
    assert normalize_persian("من نمی دانم کتاب ها کجاست") == "من نمی‌دانم کتاب‌ها کجاست"


def test_punctuation_spacing_is_normalized() -> None:
    assert normalize_persian("سلام ،خوبی ؟") == "سلام، خوبی؟"


def test_punctuation_is_only_added_when_missing() -> None:
    assert ensure_punctuation("سلام") == "سلام."
    assert ensure_punctuation("سلام؟") == "سلام؟"
