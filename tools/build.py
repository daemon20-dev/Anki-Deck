"""Assemble the Anki templates from src/.

    python3 tools/build.py

Writes the files you paste into Anki — front.html / back.html / styling.css
for the basic deck, and cloze/front.html / cloze/back.html / cloze/styling.css
for the cloze deck — by
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


# Basic deck (Front / Back / Explanation) → repo root
# Cloze deck  (Text / Back Extra)        → cloze/
TEMPLATES = {
    "front.html": "front.html",
    "back.html": "back.html",
    "cloze/front.html": "cloze/front.html",
    "cloze/back.html": "cloze/back.html",
}

for src, dest in TEMPLATES.items():
    out = HEADER + expand((SRC / src).read_text(encoding="utf-8"))
    (ROOT / dest).write_text(out, encoding="utf-8")
    print(f"wrote {dest}")

# The cloze styling is the shared styling plus the cloze-specific rules.
css = (ROOT / "styling.css").read_text(encoding="utf-8")
cloze_css = (SRC / "cloze" / "cloze.css").read_text(encoding="utf-8")
(ROOT / "cloze" / "styling.css").write_text(css.rstrip("\n") + "\n" + cloze_css, encoding="utf-8")
print("wrote cloze/styling.css")
