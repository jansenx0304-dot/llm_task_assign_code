from __future__ import annotations

import json
import sys
from typing import Any, Iterable

LINE_WIDTH = 88


def section(title: str, icon: str = "📌") -> None:
    line = _line("═", "=")
    _emit("")
    _emit(line)
    _emit(f"{_safe_icon(icon, '[SECTION]')} {title}")
    _emit(line)


def subsection(title: str, icon: str = "•") -> None:
    line = _line("─", "-")
    _emit("")
    _emit(line)
    _emit(f"{_safe_icon(icon, '[DETAIL]')} {title}")
    _emit(line)


def kv(label: str, value: Any, icon: str = "•") -> None:
    rendered = _stringify(value).splitlines() or [""]
    prefix = f"{_safe_icon(icon, '-')} {label:<24} "
    _emit(prefix + rendered[0])
    for line in rendered[1:]:
        _emit(" " * len(prefix) + line)


def info(message: str) -> None:
    _emit(f"{_safe_icon('ℹ️', '[INFO]')} {message}")


def success(message: str) -> None:
    _emit(f"{_safe_icon('✅', '[OK]')} {message}")


def warning(message: str) -> None:
    _emit(f"{_safe_icon('⚠️', '[WARN]')} {message}")


def stop(message: str) -> None:
    _emit(f"{_safe_icon('🛑', '[STOP]')} {message}")


def text_block(title: str, text: str, icon: str = "📄") -> None:
    subsection(title, icon=icon)
    _emit((text or "").rstrip() or "(empty)")


def json_block(title: str, data: Any, icon: str = "🧾") -> None:
    text_block(
        title=title,
        text=json.dumps(data, ensure_ascii=False, indent=2),
        icon=icon,
    )


def bullets(title: str, items: Iterable[str], icon: str = "📋") -> None:
    subsection(title, icon=icon)
    has_item = False
    for item in items:
        has_item = True
        _emit(f"  {_safe_icon('•', '-')} {item}")
    if not has_item:
        _emit(f"  {_safe_icon('•', '-')} (empty)")


def _stringify(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            pass
    return str(value)


def _emit(text: str) -> None:
    print(_sanitize(text))


def _sanitize(text: str) -> str:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def _safe_icon(icon: str, fallback: str) -> str:
    if not _prefer_unicode():
        return fallback
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        icon.encode(encoding)
        return icon
    except Exception:
        return fallback


def _line(unicode_char: str, ascii_char: str) -> str:
    if _prefer_unicode():
        return unicode_char * LINE_WIDTH
    return ascii_char * LINE_WIDTH


def _prefer_unicode() -> bool:
    encoding = (getattr(sys.stdout, "encoding", None) or "").lower()
    return "utf" in encoding
