"""Assemble the Anki templates from src/.

    python3 tools/build.py

Writes front.html and back.html (the files you paste into Anki) by
expanding `<!-- @include name -->` lines with the matching file in src/.
The night scene lives once in src/scene.html, so front and back can
never drift apart.
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
INCLUDE = re.compile(r"^<!-- @include ([\w.-]+) -->\n", re.M)
HEADER = "<!-- Generated from src/ by tools/build.py — edit src/, then rebuild. -->\n"


def include(name: str) -> str:
    text = (SRC / name).read_text(encoding="utf-8")
    # Stamp the scene with a hash of its own markup, so a live scene kept from
    # an older version of the template is replaced instead of reused.
    version = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return text.replace("@SCENE_VERSION@", version)


def expand(text: str) -> str:
    return INCLUDE.sub(lambda m: include(m.group(1)), text)


for name in ("front.html", "back.html"):
    out = HEADER + expand((SRC / name).read_text(encoding="utf-8"))
    (ROOT / name).write_text(out, encoding="utf-8")
    print(f"wrote {name}")
