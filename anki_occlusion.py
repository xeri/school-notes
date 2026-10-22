#!/usr/bin/env python3
"""Turn a labelled notes/*.svg diagram into an Anki Image Occlusion note.

    python anki_occlusion.py T4-PHQ/notes/phys-transformer.svg [more.svg ...]

For each diagram it renders a PNG next to the other build output (pdf/occlusion/),
finds every <text> label in the SVG, and writes pdf/occlusion/<name>.json holding
the fields for Anki's built-in "Image Occlusion" note type: one rectangle mask per
label, each its own cloze, so the card hides one label at a time. Titles, captions
and bare axis numbers are left visible.

The JSON is what Claude (through the anki-mcp server) feeds to store_media_file and
add_notes; see ANKI.md. Nothing here talks to Anki directly.
"""

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "pdf" / "occlusion"
TYPST = ROOT / "local" / "toolchain" / "typst-x86_64-pc-windows-msvc" / "typst.exe"
NS = "{http://www.w3.org/2000/svg}"
ACCENT = "#c800ff"  # the project accent, as in build.py

NUMERIC = re.compile(r"^[\s\d.,%$°−\-+×/()]*$")


def walk(el, inherited, out):
    attrs = dict(inherited)
    for key in ("font-size", "text-anchor", "font-weight"):
        if el.get(key):
            attrs[key] = el.get(key)
    style = el.get("style", "")
    for key in ("font-size", "text-anchor", "font-weight"):
        m = re.search(key + r"\s*:\s*([^;]+)", style)
        if m:
            attrs[key] = m.group(1).strip()
    tx, ty = attrs.get("dx", 0.0), attrs.get("dy", 0.0)
    tr = el.get("transform", "")
    if "rotate" in tr or "matrix" in tr or "scale" in tr:
        return  # rotated labels (axis titles) stay visible
    m = re.search(r"translate\(\s*([-\d.]+)[ ,]*([-\d.]*)", tr)
    if m:
        tx += float(m.group(1))
        ty += float(m.group(2) or 0)
    attrs["dx"], attrs["dy"] = tx, ty
    if el.tag == NS + "text":
        text = "".join(el.itertext()).strip()
        if text:
            out.append((text, el, attrs))
        return
    for child in el:
        walk(child, attrs, out)


def label_boxes(svg_path):
    root = ET.parse(svg_path).getroot()
    vb = [float(v) for v in root.get("viewBox", f"0 0 {root.get('width')} {root.get('height')}").split()]
    W, H = vb[2], vb[3]
    found = []
    walk(root, {"font-size": "16", "text-anchor": "start", "font-weight": "normal"}, found)
    boxes, titles = [], []
    for text, el, a in found:
        fs = float(re.sub(r"[^\d.]", "", a["font-size"]) or 16)
        x = float(el.get("x", 0)) + a["dx"] - vb[0]
        y = float(el.get("y", 0)) + a["dy"] - vb[1]
        bold = a["font-weight"] in ("bold", "600", "700", "800")
        w = len(text) * fs * (0.60 if bold else 0.55)
        h = fs * 1.2
        anchor = el.get("text-anchor", a["text-anchor"])
        left = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        top = y - fs * 0.9
        # leave titles, long captions and bare numbers (axis ticks) visible
        if NUMERIC.match(text):
            continue
        if top < H * 0.06 and (bold or fs >= 18):
            titles.append((text, left, top, w, h, ("title", round(x)), y))
            continue
        if top > H * 0.88 and len(text) > 40:
            continue
        if len(text) > 60:  # an explanatory sentence, not a label
            continue
        if re.search(r"\bper\b", text) and len(text) < 32:  # axis title: "Price ($ per unit)"
            continue
        # a label written as several stacked lines is one answer, so one mask
        prev = boxes[-1] if boxes else None
        if (prev and prev[5] == (anchor, round(x)) and 0 < y - prev[6] <= fs * 1.6):
            ptext, pl, pt, pw, ph, key, _ = prev
            nl, nr = min(pl, left), max(pl + pw, left + w)
            boxes[-1] = (ptext + " " + text, nl, pt, nr - nl, top + h - pt, key, y)
        else:
            boxes.append((text, left, top, w, h, (anchor, round(x)), y))
    # a title that lists two or more of the answers would give them away: mask it too
    answers = [b[0].lower() for b in boxes]
    for t in titles:
        if sum(1 for a in answers if len(a) > 2 and a in t[0].lower()) >= 2:
            boxes.insert(0, t)
    pad = 3
    return W, H, [
        (t, max(l - pad, 0) / W, max(tp - pad, 0) / H, min(w + 2 * pad, W) / W, min(h + 2 * pad, H) / H)
        for t, l, tp, w, h, _, _ in boxes
    ]


def deck_for(svg_path):
    """the deck of the topic page that embeds this diagram."""
    d = svg_path.parent.parent
    for md in sorted((d / "notes").glob("*.md")):
        if svg_path.name in md.read_text(encoding="utf-8"):
            deck = d / "anki" / f"{md.stem}.txt"
            if deck.exists():
                for line in deck.read_text(encoding="utf-8").splitlines():
                    if line.startswith("#deck:"):
                        return line[6:].strip(), md.stem
    return None, None


def render_png(svg_path, W):
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f"{svg_path.stem}.png"
    typ = OUT / f"{svg_path.stem}.typ"
    rel = Path("..", "..", svg_path.relative_to(ROOT)).as_posix()
    typ.write_text(
        f'#set page(width: {W}pt, height: auto, margin: 0pt)\n#image("{rel}", width: {W}pt)\n',
        encoding="utf-8",
    )
    subprocess.run([str(TYPST), "compile", "--root", str(ROOT), str(typ), str(png),
                    "--format", "png", "--ppi", "144"], check=True)
    typ.unlink()
    return png


def build(svg):
    svg_path = Path(svg).resolve()
    W, H, boxes = label_boxes(svg_path)
    if not boxes:
        print(f"{svg_path.name}: no maskable labels, skipped")
        return
    png = render_png(svg_path, W)
    deck, page = deck_for(svg_path)
    media = f"preq-{svg_path.stem}.png"
    occl = "<br>".join(
        f"{{{{c{i}::image-occlusion:rect:left={l:.4f}:top={t:.4f}:width={w:.4f}:height={h:.4f}:oi=1}}}}"
        for i, (_, l, t, w, h) in enumerate(boxes, 1)
    )
    subject = svg_path.parent.parent.name[3:].lower()
    note = {
        "svg": str(svg_path.relative_to(ROOT)),
        "png": str(png),
        "media_filename": media,
        "deck": deck,
        "tags": ["image-occlusion", subject] + ([page] if page else []),
        "labels": [b[0] for b in boxes],
        "fields": {
            "Occlusion": occl,
            "Image": f'<img src="{media}">',
            "Header": svg_path.stem.split("-", 1)[-1].replace("-", " ").capitalize(),
            "Back Extra": "",
            "Comments": "Generated by anki_occlusion.py from " + svg_path.name,
        },
    }
    (OUT / f"{svg_path.stem}.json").write_text(json.dumps(note, indent=1, ensure_ascii=False), encoding="utf-8")
    preview(svg_path, W, H, boxes)
    print(f"{svg_path.name}: {len(boxes)} masks -> {deck}")


def preview(svg_path, W, H, boxes):
    """pdf/occlusion/<name>-masks.png: the diagram with every mask drawn on, to check alignment."""
    rects = "".join(
        f'<rect x="{l * W:.1f}" y="{t * H:.1f}" width="{w * W:.1f}" height="{h * H:.1f}" '
        f'fill="{ACCENT}" fill-opacity="0.35" stroke="{ACCENT}" stroke-width="1.5"/>'
        for _, l, t, w, h in boxes
    )
    src = svg_path.read_text(encoding="utf-8")
    tmp = OUT / f"{svg_path.stem}-masks.svg"
    tmp.write_text(src[: src.rindex("</svg>")] + rects + "</svg>", encoding="utf-8")
    typ = OUT / f"{svg_path.stem}-masks.typ"
    typ.write_text(f'#set page(width: {W}pt, height: auto, margin: 0pt)\n#image("{tmp.name}", width: {W}pt)\n',
                   encoding="utf-8")
    subprocess.run([str(TYPST), "compile", str(typ), str(OUT / f"{svg_path.stem}-masks.png"),
                    "--format", "png", "--ppi", "72"], check=True)
    typ.unlink()
    tmp.unlink()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for a in sys.argv[1:]:
        build(a)
