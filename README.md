# Moonlit Hills — Anki card theme

A modern, sleek Anki note type styling: a frosted-glass card floating over a subtle,
**looping night scene** — rolling hills, pines, a cabin with a flickering warm window,
a soft moon, faint twinkling stars, drifting cumulus clouds and mist, fireflies and the
occasional shooting star.

Shadows lean **dark blue**. The scene keeps a few warm orange accents (moon, cabin,
fireflies); the card itself uses cool white highlights only.

| Answer (desktop) | Answer (phone) |
| --- | --- |
| ![desktop](docs/preview-desktop.png) | ![phone](docs/preview-phone.png) |

## Files

| File | Paste into (Tools → Manage Note Types → Cards…) |
| --- | --- |
| `front.html` | **Front Template** |
| `back.html`  | **Back Template** |
| `styling.css` | **Styling** |

The note type needs the fields **Front**, **Back** and **Explanation**.

## Features

- **Seamless background** — every scene animation runs off one shared clock, so the
  sky keeps moving smoothly when the card flips instead of restarting.
- **Answer reveal** slides open with pure CSS (no height measuring in JS).
- **Explanation drawer** — click the button, press **H** on desktop, or bind
  AnkiDroid's *User Action 1* (`userJs1`). The button is disabled when the card has no
  explanation, and appears (disabled) on the front so the layout never shifts.
  It sits centred under the card.
- **Responsive** — no fixed `min-width`s; works on phones (AnkiDroid / AnkiMobile).
- **Accessible** — honours the OS *reduce motion* setting, keyboard focus styles,
  `aria-expanded` on the toggle.
- Optional HUD (`#gm-time-box`, `#gm-streak-box`) and milestone overlay
  (`#gm-milestone`) styles are kept for add-ons/scripts that inject them.

## What changed vs. the old "Dark Console" theme

- Hard-coded `min-width: 680px / 568px` removed — the card no longer overflows on mobile.
- ~80 lines of height-measuring JS replaced by CSS `grid-template-rows` transitions.
- Hotkey handler no longer captures stale DOM nodes between cards and ignores
  modifier keys / text inputs.
- Duplicate `{{^Explanation}}` button branch removed; one footer button for every card.
- All colours, radii and shadows are CSS custom properties at the top of `styling.css`
  — tweak the palette in one place.

## Local preview

```sh
python3 preview/build.py   # writes preview/front.html and preview/back.html
```

Open the generated files in a browser (press **H** on the back preview).
