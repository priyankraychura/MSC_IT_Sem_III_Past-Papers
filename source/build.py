#!/usr/bin/env python3
"""Build the solved-paper pages from source/content/<paper>/.

    pip install markdown
    python3 source/build.py [--fragments DIR]

Each paper folder holds meta.json and q1.md .. q5.md. Writes a standalone page per
paper to solutions/. With --fragments, also writes the same page without the
<html>/<head>/<body> skeleton (the form an artifact host expects) to DIR.

Content format (one file per question):
    @@Q 1 | Topic of the question
    @@S A                      section letter: A (4 x 1 mark), B (2), C (3), D (5)
    @@I Question text          `code`, **bold** and [[blank answer]] work here
    @@TF True                  optional, for True/False items
    ...markdown answer...
    %%COPY nodejs-2024/q1.md|Question text%%   reuse an answer from another paper
"""
import html
import json
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"
PAPERS = ["angular-2024", "flutter-2024", "nodejs-2024", "nodejs-2025"]

# letter: (title, rule, section total, marks per item, expected items)
SECTIONS = {
    "A": ("Answer the following", "Attempt all · 1 mark each", 4, 1, 4),
    "B": ("Answer in brief", "Any one out of two", 2, 2, 2),
    "C": ("Answer in detail", "Any one out of two", 3, 3, 2),
    "D": ("Write a note on", "Any one out of two", 5, 5, 2),
}

# fence language: (highlight.js class, label shown on the block)
LANGS = {
    "js": ("javascript", "JavaScript"), "ts": ("typescript", "TypeScript"),
    "html": ("xml", "HTML"), "dart": ("dart", "Dart"), "bash": ("bash", "Terminal"),
    "json": ("json", "JSON"), "yaml": ("yaml", "YAML"), "sql": ("sql", "SQL"),
    "ejs": ("xml", "EJS template"), "pug": ("plaintext", "Pug template"),
    "xml": ("xml", "XML"), "css": ("css", "CSS"), "output": ("plaintext", "Output"),
    "text": ("plaintext", "Text"), "tree": ("plaintext", "Folder structure"),
    "console": ("plaintext", "Terminal session"),
}

CHECK_SVG = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.5" '
             'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
             'stroke-linejoin="round"/></svg>')


def inline(text):
    """Question text: escape, then blanks, inline code and bold."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\[\[(.+?)\]\]", r'<span class="blank"><span class="fill">\1</span></span>', out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)


def code_block(match):
    lang = match.group(1)
    if lang not in LANGS:
        raise ValueError(f"unknown code language: {lang}")
    cls, label = LANGS[lang]
    kind = ' data-kind="output"' if lang == "output" else ""
    return (f'<div class="code"{kind}><div class="code-bar"><span>{label}</span>'
            f'<button type="button" class="copy">Copy</button></div>'
            f'<pre><code class="language-{cls}">{match.group(2)}</code></pre></div>')


def render_md(text):
    out = markdown.markdown(text, extensions=["fenced_code", "tables", "sane_lists"])
    out = re.sub(r'<pre><code class="language-([\w-]+)">(.*?)</code></pre>', code_block, out, flags=re.S)
    if "<pre><code>" in out:
        raise ValueError("code fence without a language")
    out = re.sub(r"<table>(.*?)</table>", wrap_table, out, flags=re.S)
    return re.sub(r'<svg class="dg" viewBox="0 0 (\d+) (\d+)"', size_diagram, out)


def wrap_table(match):
    head = match.group(1).split("</tr>", 1)[0]
    return f'<div class="table-wrap cols-{head.count("<th")}"><table>{match.group(1)}</table></div>'


def size_diagram(match):
    # Draw at about 1.15x on wide screens; on phones scale down to fit (a 460-wide
    # drawing still fits a 390px screen) rather than hide part of the picture.
    w = int(match.group(1))
    return (f'<svg class="dg" style="--dw: {round(w * 1.15)}px; --dmin: {round(w * 0.74)}px" '
            f'viewBox="0 0 {w} {match.group(2)}"')


def weight(m):
    label = "mark" if m == 1 else "marks"
    return (f'<span class="wt" data-m="{m}" aria-label="{m} {label}"><b>{m}</b>'
            f'<span class="bars" aria-hidden="true">{"<i></i>" * 5}</span></span>')


def render_item(item, qno, letter, idx, marks):
    iid = f"q{qno}{letter.lower()}{idx}"
    body = "\n".join(item["body"]).strip()
    ans = ""
    if item["tf"]:
        ok = item["tf"].lower() == "true"
        ans += (f'<p class="verdict"><span class="pill {"pill-true" if ok else "pill-false"}">'
                f'{"True" if ok else "False"}</span></p>')
    if body:
        ans += render_md(body)
    ans_html = f'<div class="ans">{ans}</div>' if ans else ""
    label = f"Q{qno} ({letter}) {idx}"
    return (f'<article class="item" id="{iid}" data-marks="{marks}">'
            f'<div class="item-no" aria-hidden="true">{idx}</div>'
            f'<div class="item-main"><p class="ask">{inline(item["ask"])}</p>'
            f'{ans_html}<button type="button" class="reveal">Show answer</button></div>'
            f'<div class="item-side">{weight(marks)}'
            f'<button type="button" class="done" aria-pressed="false" aria-label="Mark {label} as revised" '
            f'title="Mark as revised">{CHECK_SVG}</button></div></article>')


def render_question(q):
    parts = []
    for sec in q["secs"]:
        letter = sec["letter"]
        title, rule, total, each, _ = SECTIONS[letter]
        items = []
        for i, it in enumerate(sec["items"], 1):
            if i > 1 and letter != "A":
                items.append('<div class="or" aria-hidden="true">or</div>')
            items.append(render_item(it, q["no"], letter, i, each))
        parts.append(
            f'<section class="sec" id="q{q["no"]}{letter.lower()}" data-marks="{each}">'
            f'<header class="sec-head"><span class="sec-letter">({letter})</span>'
            f'<h3 class="sec-title">{title}</h3><span class="sec-rule">{rule}</span>'
            f'<span class="sec-marks" aria-label="{total} marks">{total}</span></header>'
            f'<div class="items">{"".join(items)}</div></section>')
    return (f'<section class="q" id="q{q["no"]}" aria-labelledby="q{q["no"]}-title">'
            f'<header class="q-head"><p class="q-no">Q.{q["no"]}</p>'
            f'<h2 id="q{q["no"]}-title">{html.escape(q["topic"])}</h2><p class="q-total">14 marks</p></header>'
            f'{"".join(parts)}</section>')


def parse_question(path):
    q, sec, item = None, None, None
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        where = f"{path.name}:{n}"
        if line.startswith("@@Q "):
            no, topic = (s.strip() for s in line[4:].split("|", 1))
            q = {"no": int(no), "topic": topic, "secs": []}
        elif line.startswith("@@S "):
            sec = {"letter": line[4:].strip(), "items": []}
            q["secs"].append(sec)
            item = None
        elif line.startswith("@@I "):
            item = {"ask": line[4:].strip(), "tf": None, "body": []}
            sec["items"].append(item)
        elif line.startswith("@@TF "):
            item["tf"] = line[5:].strip()
        elif line.startswith("@@"):
            raise ValueError(f"{where}: unknown marker")
        elif item is not None:
            item["body"].append(line)
        elif line.strip():
            raise ValueError(f"{where}: text outside an item")
    for s in q["secs"]:
        for it in s["items"]:
            body = "\n".join(it["body"]).strip()
            if body.startswith("%%COPY ") and body.endswith("%%"):
                it.update(copy_answer(body[7:-2]))
    letters = [s["letter"] for s in q["secs"]]
    if letters != ["A", "B", "C", "D"]:
        raise ValueError(f"{path}: sections are {letters}")
    for s in q["secs"]:
        want = SECTIONS[s["letter"]][4]
        if len(s["items"]) != want:
            raise ValueError(f"{path}: section {s['letter']} has {len(s['items'])} items, expected {want}")
    return q


def copy_answer(ref):
    """Return body and tf of the item whose question matches, from another content file."""
    rel, ask = (part.strip() for part in ref.split("|", 1))
    source = parse_question(SRC / "content" / rel)
    for sec in source["secs"]:
        for it in sec["items"]:
            if it["ask"] == ask:
                return {"body": it["body"], "tf": it["tf"]}
    raise ValueError(f"COPY: no question {ask!r} in {rel}")


def palette(tokens):
    return " ".join(f"--{k.replace('_', '-')}: {v};" for k, v in tokens.items())


def build(slug, template):
    folder = SRC / "content" / slug
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    questions = [parse_question(folder / f"q{i}.md") for i in range(1, 6)]
    count = sum(len(s["items"]) for q in questions for s in q["secs"])
    qnav = "".join(f'<a href="#q{q["no"]}" title="{html.escape(q["topic"])}">Q{q["no"]}</a>' for q in questions)
    extra = "".join(
        f'<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/{lang}.min.js"></script>'
        for lang in meta.get("hljs_extra", []))
    page = template
    for key, value in {
        "TITLE": html.escape(meta["title"]), "LIGHT": palette(meta["light"]), "DARK": palette(meta["dark"]),
        "SLUG": slug, "CODE": html.escape(meta["code"]), "SESSION": html.escape(meta["session"]),
        "SUBJECT": html.escape(meta["subject"]), "PRINTED": html.escape(meta["printed"]),
        "TIME": html.escape(meta["time"]), "TOTAL": meta["total"], "COUNT": str(count), "QNAV": qnav,
        "EXTRA_SCRIPTS": extra, "QUESTIONS": "\n".join(render_question(q) for q in questions),
    }.items():
        page = page.replace(f"%%{key}%%", value)
    if "%%" in page:
        raise ValueError(f"{slug}: unreplaced placeholder near {page[page.index('%%'):][:40]!r}")
    return meta, page, count


def standalone(meta, fragment):
    head_end = fragment.index('<div class="app"')
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<meta name="description" content="{html.escape(meta["description"])}">\n'
            f'{fragment[:head_end]}</head>\n<body>\n{fragment[head_end:]}</body>\n</html>\n')


def main():
    fragments = None
    if "--fragments" in sys.argv:
        fragments = Path(sys.argv[sys.argv.index("--fragments") + 1])
        fragments.mkdir(parents=True, exist_ok=True)
    template = (SRC / "template.html").read_text(encoding="utf-8")
    (ROOT / "solutions").mkdir(exist_ok=True)
    for slug in PAPERS:
        if not (SRC / "content" / slug / "q5.md").exists():
            print(f"skip {slug}: content not complete")
            continue
        meta, page, count = build(slug, template)
        (ROOT / "solutions" / f"{meta['file']}.html").write_text(standalone(meta, page), encoding="utf-8")
        if fragments:
            (fragments / f"{meta['file']}.html").write_text(page, encoding="utf-8")
        print(f"built {meta['file']}: {count} answers, {len(page) // 1024} KB")


if __name__ == "__main__":
    main()
