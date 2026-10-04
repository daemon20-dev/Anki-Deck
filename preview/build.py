"""Build preview/front.html and preview/back.html with sample content.

Usage:  python3 preview/build.py   then open the generated files in a browser.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAMPLE = {
    "Front": "What is the <b>powerhouse</b> of the cell?",
    "Back": "The <b>mitochondria</b> — it produces ATP through <i>cellular respiration</i>.",
    "Explanation": "Mitochondria have their own DNA and a double membrane. The inner membrane "
                   "folds into <b>cristae</b>, increasing surface area for the electron transport chain.",
}

css = (ROOT / "styling.css").read_text(encoding="utf-8")
for side in ("front", "back"):
    html = (ROOT / f"{side}.html").read_text(encoding="utf-8")
    # Keep {{#Explanation}} blocks, drop {{^Explanation}} blocks (field is filled).
    html = re.sub(r"\{\{\^(\w+)\}\}.*?\{\{/\1\}\}", "", html, flags=re.S)
    html = re.sub(r"\{\{[#/]\w+\}\}", "", html)
    for field, value in SAMPLE.items():
        html = html.replace("{{%s}}" % field, value)
    page = (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<style>{css}</style></head><body class=\"card card1\">{html}</body></html>"
    )
    (ROOT / "preview" / f"{side}.html").write_text(page, encoding="utf-8")
    print(f"wrote preview/{side}.html")
