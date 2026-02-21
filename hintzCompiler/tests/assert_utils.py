# Copyright (c) 2024–2025 Kumar Aakash. Released under the MIT License.

def _normalize_whitespace(value: str) -> str:
    return "".join(str(value).split())

def assertContains(actual: str, expected: str):
    norm_actual = _normalize_whitespace(actual)
    norm_expected = _normalize_whitespace(expected)

    if norm_expected in norm_actual or norm_actual in norm_expected:
        return

    msg = (
        f"\n\n[[-- FAILED --]]\nExpected:||{expected.strip()}||"
        f"\n\nActual:||{actual}||"
    )
    raise AssertionError(msg)
