from __future__ import annotations

import json
import sys
from typing import Any, Iterable

LINE_WIDTH = 88


def section(title: str, icon: str = "section") -> None:
    del icon
    line = "=" * LINE_WIDTH
    _emit("")
    _emit(line)
    _emit(f"[SECTION] {title}")
    _emit(line)


def subsection(title: str, icon: str = "detail") -> None:
    del icon
    _emit("")
    _emit(f"[SUBSECTION] {title}")
    _emit("-" * LINE_WIDTH)


def kv(label: str, value: Any, icon: str = "item") -> None:
    del icon
    rendered = _stringify(value).splitlines() or [""]
    prefix = f"  - {label}: "
    _emit(prefix + rendered[0])
    for line in rendered[1:]:
        _emit(" " * len(prefix) + line)


def info(message: str) -> None:
    _emit(f"[INFO] {message}")


def success(message: str) -> None:
    _emit(f"[OK] {message}")


def warning(message: str) -> None:
    _emit(f"[WARN] {message}")


def error(message: str) -> None:
    _emit(f"[ERROR] {message}")


def stop(message: str) -> None:
    _emit(f"[STOP] {message}")


def text_block(title: str, text: str, icon: str = "text") -> None:
    del icon
    _emit("")
    _emit(f"[BEGIN] {title}")
    _emit("-" * LINE_WIDTH)
    _emit((text or "").rstrip() or "(empty)")
    _emit("-" * LINE_WIDTH)
    _emit(f"[END] {title}")


def json_block(title: str, data: Any, icon: str = "json") -> None:
    del icon
    text_block(
        title=title,
        text=json.dumps(data, ensure_ascii=False, indent=2),
    )


def bullets(title: str, items: Iterable[str], icon: str = "list") -> None:
    del icon
    subsection(title)
    has_item = False
    for item in items:
        has_item = True
        _emit(f"  - {item}")
    if not has_item:
        _emit("  - (empty)")


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
