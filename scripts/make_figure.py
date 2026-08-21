"""Render the README example figure from the actual dataset files.

    python scripts/make_figure.py            # -> assets/example.svg
    python scripts/make_figure.py --dark     # also assets/example-dark.svg

Nothing in the figure is hand-written. The question, both supporting documents,
their English glosses and the answer are read out of data/two_hop/hotpotqa/*.jsonl.
Because the language files are positionally aligned, the English gloss is simply
the same record read from en.jsonl -- the figure demonstrates the alignment it
describes, and cannot drift away from the released data.

The example is a 2-hop bridge question: query in English, bridging document in
French, answer-bearing document in Chinese. Neither document answers alone.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RECORD = "hotpotqa_766"
QUERY, HOP1, HOP2 = "en", "fr", "zh"

LANG = {"en": "English", "zh": "Chinese", "fr": "French",
        "ar": "Arabic", "ru": "Russian"}

THEME = {
    "light": dict(bg="#ffffff", panel="#f8f9fb", ink="#161a21", muted="#5c6675",
                  line="#dfe3e9", accent="#3d5a80", bridge="#8a6d1f", ans="#2f7d68"),
    "dark": dict(bg="#0d1117", panel="#161b23", ink="#e6e9ee", muted="#8b95a5",
                 line="#2b3440", accent="#8fb0d6", bridge="#dcbc63", ans="#7fd0b8"),
}

W, PAD = 900, 26
FS, LH = 14.5, 21          # document text
GFS, GLH = 12.5, 17.5      # English gloss


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def is_cjk(ch):
    return "　" <= ch <= "鿿" or "＀" <= ch <= "￯"


def char_w(ch, fs):
    if is_cjk(ch):
        return fs
    if ch == " ":
        return fs * 0.28
    if ch in "ilj.,'!|()":
        return fs * 0.28
    if ch.isupper():
        return fs * 0.62
    return fs * 0.52


def tokenize(text, marks=None):
    """(text, mark) tokens: CJK breaks per character, everything else per word."""
    marks = marks or {}
    if marks:
        pat = "(" + "|".join(re.escape(m) for m in
                             sorted(marks, key=len, reverse=True)) + ")"
        chunks = re.split(pat, text)
    else:
        chunks = [text]
    out = []
    for chunk in chunks:
        if not chunk:
            continue
        if chunk in marks:
            out.append((chunk, marks[chunk]))
            continue
        buf = ""
        for c in chunk:
            if is_cjk(c):
                if buf:
                    out.append((buf, None)); buf = ""
                out.append((c, None))
            else:
                buf += c
                if c == " ":
                    out.append((buf, None)); buf = ""
        if buf:
            out.append((buf, None))
    return out


def wrap(tokens, max_w, fs):
    lines, cur, w = [], [], 0.0
    for tok, mark in tokens:
        tw = sum(char_w(c, fs) for c in tok)
        if w + tw > max_w and cur:
            lines.append(cur); cur, w = [], 0.0
            if not tok.strip():
                continue
        cur.append((tok, mark)); w += tw
    if cur:
        lines.append(cur)
    return lines


STYLE = {
    "bridge": lambda T: f' fill="{T["bridge"]}" font-weight="700"',
    "ans": lambda T: f' fill="{T["ans"]}" font-weight="700"',
    "label": lambda T: f' fill="{T["muted"]}" font-weight="700" font-style="normal"',
}


def text_block(x, y, tokens, max_w, T, fs=FS, lh=LH,
               fill=None, italic=False):
    lines = wrap(tokens, max_w, fs)
    style = ' font-style="italic"' if italic else ""
    out = [f'<text x="{x}" y="{y}" font-size="{fs}" '
           f'fill="{fill or T["ink"]}"{style}>']
    for k, line in enumerate(lines):
        first = True
        for tok, mark in line:
            attrs = STYLE[mark](T) if mark in STYLE else ""
            pos = f' x="{x}" dy="{0 if k == 0 else lh}"' if first else ""
            out.append(f'<tspan{pos}{attrs}>{esc(tok)}</tspan>')
            first = False
    out.append("</text>")
    return "".join(out), len(lines) * lh


def card(x, y, w, h, T, accent=None):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h:.1f}" rx="10" '
            f'fill="{T["panel"]}" stroke="{accent or T["line"]}" stroke-width="1"/>')


def chip(x, y, label, T, color):
    tw = sum(char_w(c, 10.5) for c in label) + 16
    return (f'<rect x="{x - tw:.1f}" y="{y - 12}" width="{tw:.0f}" height="18" rx="9" '
            f'fill="none" stroke="{color}" stroke-width="1" opacity=".6"/>'
            f'<text x="{x - tw + 8:.1f}" y="{y + 1}" font-size="10.5" fill="{color}">'
            f'{esc(label)}</text>')


def eyebrow(x, y, s, T, color=None):
    return (f'<text x="{x}" y="{y}" font-size="10" fill="{color or T["muted"]}" '
            f'letter-spacing="1.4" font-weight="600">{esc(s.upper())}</text>')


def gloss_tokens(gloss, marks=None):
    """Parenthesised italic translation. Labelled in place rather than only in the
    caption, so a reader who skips the caption still cannot mistake it for part of
    the context the model receives."""
    return ([("(", None), ("English meanings:", "label"), (" ", None)]
            + tokenize(gloss, marks) + [(")", None)])


def seg_height(doc, inner):
    """Height of one hop inside the shared context block."""
    n = len(wrap(tokenize(doc["text"], doc["marks"]), inner, FS))
    g = len(wrap(gloss_tokens(doc["gloss"], doc["gloss_marks"]),
                 inner, GFS)) if doc["gloss"] else 0
    return 18 + n * LH + (4 + g * GLH if g else 0)


def build(data, theme):
    T = THEME[theme]
    inner = W - 2 * PAD - 28
    parts, y = [], PAD

    # ---- question -------------------------------------------------------
    qt = tokenize(data["question"])
    qh = 30 + len(wrap(qt, inner, 16)) * 23 + 16
    parts.append(card(PAD, y, W - 2 * PAD, qh, T))
    parts.append(eyebrow(PAD + 14, y + 22, "question", T))
    parts.append(chip(W - PAD - 14, y + 21, LANG[QUERY], T, T["accent"]))
    tb, _ = text_block(PAD + 14, y + 48, qt, inner, T, fs=16, lh=23)
    parts.append(tb)
    y += qh + 14

    # ---- ONE context block, both hops inside it -------------------------
    # The model is given a single context, so showing two separate boxes would
    # misrepresent the input. The per-hop labels stay, the container does not.
    segs = [seg_height(d, inner) for d in data["docs"]]
    ch = 34 + sum(segs) + 14 * (len(segs) - 1) + 16
    parts.append(card(PAD, y, W - 2 * PAD, ch, T, T["accent"]))
    parts.append(eyebrow(PAD + 14, y + 22, "context", T, T["accent"]))
    parts.append(chip(W - PAD - 14, y + 21,
                      " + ".join(LANG[d["lang"]] for d in data["docs"]),
                      T, T["accent"]))
    sy = y + 34
    for k, doc in enumerate(data["docs"]):
        if k:
            parts.append(f'<path d="M{PAD + 14} {sy - 7} H{W - PAD - 14}" '
                         f'stroke="{T["line"]}" stroke-width="1"/>')
        parts.append(f'<text x="{PAD + 14}" y="{sy + 12}" font-size="10" '
                     f'fill="{T["muted"]}" letter-spacing="1.2" font-weight="600">'
                     f'{esc(doc["eyebrow"].upper())} &#183; {esc(LANG[doc["lang"]].upper())}'
                     f'</text>')
        tb, used = text_block(PAD + 14, sy + 34,
                              tokenize(doc["text"], doc["marks"]), inner, T)
        parts.append(tb)
        if doc["gloss"]:
            gb, _ = text_block(PAD + 14, sy + 34 + used + 4,
                               gloss_tokens(doc["gloss"], doc["gloss_marks"]),
                               inner, T, fs=GFS, lh=GLH,
                               fill=T["muted"], italic=True)
            parts.append(gb)
        sy += segs[k] + 14
    y += ch + 14

    # ---- answer ---------------------------------------------------------
    parts.append(card(PAD, y, W - 2 * PAD, 48, T, T["ans"]))
    parts.append(eyebrow(PAD + 14, y + 29, "answer", T, T["ans"]))
    parts.append(f'<text x="{PAD + 84}" y="{y + 31}" font-size="16" '
                 f'font-weight="700" fill="{T["ans"]}">{esc(data["answer"])}</text>')
    y += 48 + 12

    # ---- legend ---------------------------------------------------------
    parts.append(f'<text x="{PAD + 2}" y="{y + 10}" font-size="11.5" '
                 f'fill="{T["muted"]}">'
                 f'<tspan fill="{T["bridge"]}" font-weight="700">Bridge entity</tspan>'
                 f'<tspan> links the two hops · </tspan>'
                 f'<tspan fill="{T["ans"]}" font-weight="700">answer</tspan>'
                 f'<tspan> appears only in hop 2 · parenthesised italics give the '
                 f'English meanings and are not part of the model input</tspan></text>')
    y += 10 + PAD

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y:.0f}" '
        f'viewBox="0 0 {W} {y:.0f}" font-family="-apple-system,BlinkMacSystemFont,'
        f'&quot;Segoe UI&quot;,Roboto,&quot;Helvetica Neue&quot;,Arial,'
        f'&quot;Noto Sans&quot;,&quot;Noto Sans CJK SC&quot;,sans-serif">',
        f'<rect width="{W}" height="{y:.0f}" fill="{T["bg"]}"/>',
        *parts, "</svg>"])


def answer_span(text, gold, minlen=3):
    """Longest prefix of the gold answer occurring in the text. Handles inflection
    ("Североирландец" vs "североирландская") and CJK, where there are no word
    boundaries to match on. Returns None rather than highlighting the wrong thing."""
    tl, gl = text.lower(), gold.lower()
    for n in range(len(gl), minlen - 1, -1):
        k = tl.find(gl[:n])
        if k >= 0:
            return text[k:k + n]
    return None


def load_record():
    rec = {}
    for c in {QUERY, HOP1, HOP2}:
        rows = (json.loads(l) for l in
                open(ROOT / f"data/two_hop/hotpotqa/{c}.jsonl", encoding="utf-8"))
        rec[c] = next(r for r in rows if r["id"] == RECORD)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "assets")
    ap.add_argument("--dark", action="store_true", help="also emit a dark variant")
    a = ap.parse_args()

    rec = load_record()
    e = rec[QUERY]
    positions = e["hop_seq"]                       # [bridging, answer-bearing]

    def full(code, pos):
        return " ".join(s.strip() for s in rec[code]["answers"][pos]["sentences"])

    def mark_up(text, lang, answering):
        """Highlight the bridge entity, plus the answer on the answering hop."""
        m = {}
        bridge = rec[lang]["sub_q1"]["answer"].strip()
        if bridge and bridge in text:
            m[bridge] = "bridge"
        if answering:
            span = answer_span(text, rec[lang]["answer"].strip())
            if span and span not in m:
                m[span] = "ans"
        return m

    docs = []
    for k, (lang, pos) in enumerate(zip((HOP1, HOP2), positions)):
        text = full(lang, pos)
        gloss = full(QUERY, pos) if lang != QUERY else None
        docs.append({
            "eyebrow": "hop 1 · bridging" if k == 0 else "hop 2 · answer-bearing",
            "lang": lang, "text": text, "gloss": gloss,
            "marks": mark_up(text, lang, k == 1),
            # the gloss is English, so it is marked against the English record
            "gloss_marks": mark_up(gloss, QUERY, k == 1) if gloss else {},
            "answering": k == 1,
        })

    data = {"question": e["question"], "answer": e["answer"], "docs": docs}

    a.out.mkdir(parents=True, exist_ok=True)
    for theme in (["light", "dark"] if a.dark else ["light"]):
        p = a.out / ("example.svg" if theme == "light" else "example-dark.svg")
        p.write_text(build(data, theme), encoding="utf-8")
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")

    print(f"\nrecord {RECORD}   query={LANG[QUERY]} "
          f"hop1={LANG[HOP1]} hop2={LANG[HOP2]}")
    for d in docs:
        print(f"  {d['eyebrow']:<24} {d['lang']}  marks={list(d['marks'])}")
    print(f"  answer: {data['answer']}")


if __name__ == "__main__":
    main()
