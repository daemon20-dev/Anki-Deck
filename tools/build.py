"""Assemble the Anki templates from src/.

    python3 tools/build.py

Writes front.html and back.html (the files you paste into Anki) by
expanding `<!-- @include name -->` lines with the matching file in src/.
The night scene lives once in src/scene.html, so front and back can
never drift apart.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
INCLUDE = re.compile(r"^<!-- @include ([\w.-]+) -->\n", re.M)
HEADER = "<!-- Generated from src/ by tools/build.py — edit src/, then rebuild. -->\n"


def expand(text: str) -> str:
    return INCLUDE.sub(lambda m: (SRC / m.group(1)).read_text(encoding="utf-8"), text)


for name in ("front.html", "back.html"):
    out = HEADER + expand((SRC / name).read_text(encoding="utf-8"))
    (ROOT / name).write_text(out, encoding="utf-8")
    print(f"wrote {name}")
