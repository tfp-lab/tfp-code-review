#!/usr/bin/env python3
"""
md2html.py — 人間に見せるための Markdown → HTML 変換ツール (標準ライブラリのみ)

使い方:
    python3 .claude/scripts/md2html.py <input.md> [-o <output.html>]

外部依存ゼロで動くよう、最低限の Markdown サブセットを実装している:
- ATX 見出し (# / ## / ###)
- 段落 (空行区切り)
- コードブロック (``` 囲み、言語タグ対応)
- インラインコード (` 囲み)
- 強調 (**bold**, *italic*)
- リンク [text](url)
- 順序なしリスト (- / *)
- 順序付きリスト (1. 2. ...)
- テーブル (GFM 風)
- 水平線 (---)
- 引用 (>)

出力先デフォルトは `<input_dir>/_html/<input_stem>.html` (gitignore 推奨)。
HTML には日本語が読みやすい控えめな CSS を埋め込む。
"""
from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import os
import re
import sys
from pathlib import Path


CSS = """\
/*
 * Modern documentation theme inspired by Linear / Anthropic docs / Vercel docs.
 * Optimized for Japanese reading: generous line-height, palt kerning, IBM Plex JP fallback.
 */

:root {
  /* Neutrals (warm, not pure gray) */
  --neutral-0: #ffffff;
  --neutral-50: #fafaf9;
  --neutral-100: #f5f5f4;
  --neutral-150: #ececea;
  --neutral-200: #e7e5e4;
  --neutral-300: #d6d3d1;
  --neutral-500: #78716c;
  --neutral-600: #57534e;
  --neutral-700: #44403c;
  --neutral-800: #292524;
  --neutral-900: #1c1917;
  --neutral-950: #0c0a09;

  /* Accent: deep indigo (works well in light + dark) */
  --accent-300: #a5b4fc;
  --accent-500: #6366f1;
  --accent-600: #4f46e5;
  --accent-700: #4338ca;
  --accent-bg: #eef2ff;

  /* Surface tokens */
  --bg: var(--neutral-0);
  --bg-elevated: var(--neutral-50);
  --bg-subtle: var(--neutral-100);
  --bg-code: var(--neutral-50);
  --fg: var(--neutral-800);
  --fg-strong: var(--neutral-950);
  --fg-muted: var(--neutral-500);
  --border: var(--neutral-200);
  --border-strong: var(--neutral-300);
  --link: var(--accent-600);
  --link-hover: var(--accent-700);
  --selection: var(--accent-bg);

  /* Shadows: more elevation than before */
  --shadow-sm: 0 1px 2px rgba(28, 25, 23, 0.04);
  --shadow-md: 0 1px 3px rgba(28, 25, 23, 0.06), 0 4px 12px rgba(28, 25, 23, 0.04);
  --shadow-lg: 0 4px 6px rgba(28, 25, 23, 0.05), 0 12px 24px rgba(28, 25, 23, 0.06);

  /* Radii (consistent system) */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0a0a0a;
    --bg-elevated: #141414;
    --bg-subtle: #1a1a1a;
    --bg-code: #131313;
    --fg: #d4d4d8;
    --fg-strong: #fafafa;
    --fg-muted: #71717a;
    --border: #27272a;
    --border-strong: #3f3f46;
    --accent-bg: rgba(99, 102, 241, 0.12);
    --link: #818cf8;
    --link-hover: #a5b4fc;
    --selection: rgba(99, 102, 241, 0.3);
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.5);
  }
}

/* ── Reset & base ───────────────────────────────────────── */

*, *::before, *::after { box-sizing: border-box; }

html {
  font-size: 16px;
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
  -moz-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

body {
  margin: 0;
  padding: 0;
  color: var(--fg);
  background: var(--bg);
  font-family:
    "Inter", -apple-system, BlinkMacSystemFont,
    "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Noto Sans JP",
    "Yu Gothic", "Segoe UI", Roboto, sans-serif;
  font-feature-settings: "palt" 1, "ss02" 1, "cv11" 1;
  font-variant-ligatures: contextual common-ligatures;
  line-height: 1.78;
  letter-spacing: 0.005em;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

::selection { background: var(--selection); color: inherit; }

.container {
  max-width: 768px;
  margin: 0 auto;
  padding: 4rem 2rem 8rem;
}

/* ── Typography: headings ───────────────────────────────── */

h1, h2, h3, h4, h5, h6 {
  color: var(--fg-strong);
  font-weight: 600;
  line-height: 1.25;
  letter-spacing: -0.018em;
  text-wrap: balance;
}

h1 {
  font-size: clamp(2rem, 1.6rem + 1.5vw, 2.5rem);
  font-weight: 700;
  letter-spacing: -0.028em;
  margin: 0 0 1.25rem;
  padding: 0;
}
h1 + p {
  font-size: 1.1rem;
  color: var(--fg-muted);
  line-height: 1.65;
  margin-top: -0.4rem;
  margin-bottom: 2.5rem;
}

h2 {
  font-size: 1.5rem;
  margin: 4rem 0 1.25rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

h3 {
  font-size: 1.2rem;
  margin: 2.5rem 0 0.75rem;
}
h4 {
  font-size: 1.05rem;
  margin: 1.75rem 0 0.5rem;
  color: var(--fg);
}
h5, h6 {
  font-size: 0.95rem;
  margin: 1.4rem 0 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--fg-muted);
  font-weight: 600;
}

/* ── Body copy ──────────────────────────────────────────── */

p { margin: 1rem 0; }
p:first-child { margin-top: 0; }

strong { color: var(--fg-strong); font-weight: 600; }
em { font-style: italic; }

/* Links: refined underline animation */
a {
  color: var(--link);
  text-decoration: none;
  background-image: linear-gradient(transparent calc(100% - 1px), currentColor 1px);
  background-repeat: no-repeat;
  background-size: 0% 100%;
  transition: background-size 0.25s cubic-bezier(0.4, 0, 0.2, 1), color 0.15s;
  padding-bottom: 1px;
}
a:hover {
  color: var(--link-hover);
  background-size: 100% 100%;
}

/* ── Code ───────────────────────────────────────────────── */

code, kbd, samp, pre {
  font-family:
    "JetBrains Mono", "SF Mono", "SFMono-Regular", "Cascadia Code",
    "Roboto Mono", Menlo, Consolas, "Liberation Mono", monospace;
  font-feature-settings: "calt" 1, "ss01" 1;
  font-variant-ligatures: contextual;
}

code {
  font-size: 0.875em;
  background: var(--bg-subtle);
  color: var(--fg-strong);
  padding: 0.13em 0.4em;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  white-space: nowrap;
}

pre {
  background: var(--bg-code);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.1rem 1.25rem;
  margin: 1.5rem 0;
  overflow-x: auto;
  font-size: 0.85rem;
  line-height: 1.65;
  box-shadow: var(--shadow-sm);
  scrollbar-width: thin;
  scrollbar-color: var(--border-strong) transparent;
}
pre::-webkit-scrollbar { height: 8px; }
pre::-webkit-scrollbar-thumb {
  background: var(--border-strong);
  border-radius: 4px;
}
pre code {
  background: transparent;
  border: none;
  padding: 0;
  font-size: inherit;
  color: var(--fg);
  white-space: pre;
}

/* ── Blockquote: callout style ─────────────────────────── */

blockquote {
  margin: 1.75rem 0;
  padding: 1rem 1.25rem;
  background: var(--accent-bg);
  border-left: 3px solid var(--accent-500);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  color: var(--fg);
  position: relative;
}
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }
blockquote strong { color: var(--accent-700); }
@media (prefers-color-scheme: dark) {
  blockquote strong { color: var(--accent-300); }
}

/* ── Lists ──────────────────────────────────────────────── */

ul, ol {
  padding-left: 1.65rem;
  margin: 1rem 0;
}
li { margin: 0.4rem 0; padding-left: 0.2rem; }
li::marker { color: var(--fg-muted); }
li > ul, li > ol { margin: 0.4rem 0; }

/* Task list */
li input[type="checkbox"] {
  margin-right: 0.55rem;
  margin-left: -1.4rem;
  transform: translateY(1px) scale(1.05);
  accent-color: var(--accent-600);
  cursor: default;
}

/* ── HR ─────────────────────────────────────────────────── */

hr {
  border: none;
  height: 1px;
  background: var(--border);
  margin: 3rem 0;
}

/* ── Tables ─────────────────────────────────────────────── */

table {
  border-collapse: collapse;
  margin: 1.75rem 0;
  width: 100%;
  display: block;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: 0.92rem;
  box-shadow: var(--shadow-sm);
  scrollbar-width: thin;
}
thead {
  background: var(--bg-subtle);
}
th, td {
  border: none;
  border-bottom: 1px solid var(--border);
  padding: 0.7rem 1rem;
  text-align: left;
  vertical-align: top;
}
th {
  font-weight: 600;
  color: var(--fg-strong);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
tbody tr:last-child td { border-bottom: none; }
tbody tr {
  transition: background-color 0.12s;
}
tbody tr:hover { background: var(--bg-elevated); }
td code, th code { white-space: nowrap; }

/* ── Page header with icon ─────────────────────────────── */

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 0 0 3rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
}
.page-header .icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  padding: 4px;
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
  box-shadow: var(--shadow-sm);
}
.page-header .title-block {
  flex: 1;
  min-width: 0;
}
.page-header .title-block .source {
  font-size: 0.75rem;
  color: var(--fg-muted);
  font-family:
    "JetBrains Mono", "SF Mono", "SFMono-Regular", monospace;
  word-break: break-all;
  letter-spacing: 0;
}

/* ── Meta (no-icon fallback) ───────────────────────────── */

.meta {
  display: inline-block;
  font-size: 0.78rem;
  color: var(--fg-muted);
  margin: 0 0 3rem;
  padding: 0.4rem 0.75rem;
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-family:
    "JetBrains Mono", "SF Mono", "SFMono-Regular", monospace;
  letter-spacing: 0;
}
.meta code {
  background: transparent;
  border: none;
  padding: 0;
  font-size: inherit;
  color: inherit;
  white-space: normal;
}

/* ── Image (when used inline as content, not header icon) ── */

img:not(.icon) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-sm);
  margin: 0.5rem 0;
}
p > img:not(.icon):only-child {
  display: block;
  margin: 1.5rem auto;
  box-shadow: var(--shadow-md);
}

/* ── Mobile ─────────────────────────────────────────────── */

@media (max-width: 720px) {
  .container { padding: 2rem 1.25rem 5rem; }
  h1 { font-size: 1.65rem; }
  h2 { font-size: 1.3rem; margin-top: 3rem; padding-top: 1.25rem; }
  h3 { font-size: 1.1rem; }
  pre { font-size: 0.78rem; padding: 0.9rem; border-radius: var(--radius-sm); }
  table { font-size: 0.85rem; }
  th, td { padding: 0.55rem 0.75rem; }
  blockquote { padding: 0.8rem 1rem; }
}

/* ── Print ──────────────────────────────────────────────── */

@media print {
  :root {
    --bg: #fff;
    --fg: #000;
    --fg-strong: #000;
    --fg-muted: #444;
    --border: #ccc;
    --bg-subtle: #f7f7f7;
  }
  body { background: #fff; color: #000; }
  .container { max-width: none; padding: 0; }
  pre, blockquote, table { box-shadow: none; break-inside: avoid; }
  h1, h2, h3 { break-after: avoid; }
  a { color: #000; background: none; text-decoration: underline; }
}
"""


def _escape(s: str) -> str:
    return html.escape(s, quote=False)


_BASE_DIR: Path | None = None


def _resolve_image_src(src: str) -> str:
    """ローカル相対パスの画像は base64 埋め込みに変換 (HTML 単体配布のため)。"""
    if re.match(r"^[a-z]+://", src) or src.startswith("data:") or src.startswith("/"):
        return src
    if _BASE_DIR is None:
        return src
    p = (_BASE_DIR / src).resolve()
    if not p.is_file():
        return src
    mime, _ = mimetypes.guess_type(p.name)
    if not mime:
        mime = "application/octet-stream"
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _inline(text: str) -> str:
    """インライン記法 (コード/強調/リンク/画像) を HTML に変換。"""
    # 1) インラインコードを先に退避 (中身のエスケープを保護)
    placeholders: list[str] = []

    def _save_code(m: re.Match) -> str:
        placeholders.append(f"<code>{_escape(m.group(1))}</code>")
        return f"\x00CODE{len(placeholders) - 1}\x00"

    text = re.sub(r"`([^`]+)`", _save_code, text)

    # 2) 画像 ![alt](src) を先に退避 (リンクと干渉しないよう)
    def _save_image(m: re.Match) -> str:
        alt = _escape(m.group(1))
        src = _resolve_image_src(m.group(2))
        placeholders.append(f'<img src="{src}" alt="{alt}"/>')
        return f"\x00CODE{len(placeholders) - 1}\x00"

    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", _save_image, text)

    # 3) 残りをエスケープ
    text = _escape(text)

    # 4) リンク [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        text,
    )

    # 4) 強調 (** > * の順)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*(?!\*)", r"<em>\1</em>", text)

    # 5) プレースホルダ (コード / 画像) 復元
    def _restore(m: re.Match) -> str:
        return placeholders[int(m.group(1))]

    text = re.sub(r"\x00CODE(\d+)\x00", _restore, text)
    return text


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    n = len(lines)

    def _flush_paragraph(buf: list[str]) -> None:
        if buf:
            out.append(f"<p>{_inline(' '.join(buf).strip())}</p>")
            buf.clear()

    paragraph: list[str] = []

    while i < n:
        line = lines[i]

        # コードブロック
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            _flush_paragraph(paragraph)
            lang = m.group(1)
            i += 1
            code_lines: list[str] = []
            while i < n and not re.match(r"^```\s*$", lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 閉じ ``` をスキップ
            code = _escape("\n".join(code_lines))
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{code}</code></pre>")
            continue

        # 水平線
        if re.match(r"^\s*---+\s*$", line):
            _flush_paragraph(paragraph)
            out.append("<hr/>")
            i += 1
            continue

        # 見出し
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            _flush_paragraph(paragraph)
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # 引用ブロック
        if line.startswith(">"):
            _flush_paragraph(paragraph)
            quote_lines: list[str] = []
            while i < n and lines[i].startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            inner = md_to_html("\n".join(quote_lines))
            out.append(f"<blockquote>{inner}</blockquote>")
            continue

        # テーブル (GFM)
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$", lines[i + 1]):
            _flush_paragraph(paragraph)

            def _parse_row(s: str) -> list[str]:
                s = s.strip().strip("|")
                return [c.strip() for c in s.split("|")]

            header = _parse_row(line)
            i += 2  # 区切り行スキップ
            rows: list[list[str]] = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_parse_row(lines[i]))
                i += 1

            out.append("<table>")
            out.append("<thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in header) + "</tr></thead>")
            out.append("<tbody>")
            for r in rows:
                out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>")
            out.append("</tbody></table>")
            continue

        # 順序なしリスト
        if re.match(r"^\s*[-*+]\s+", line):
            _flush_paragraph(paragraph)
            items: list[str] = []
            while i < n and re.match(r"^\s*[-*+]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*+]\s+", "", lines[i]))
                i += 1
            out.append("<ul>")
            for item in items:
                # チェックボックス
                cb = re.match(r"^\[([ xX])\]\s+(.*)$", item)
                if cb:
                    checked = "checked" if cb.group(1) in ("x", "X") else ""
                    out.append(
                        f'<li><input type="checkbox" disabled {checked}/> {_inline(cb.group(2))}</li>'
                    )
                else:
                    out.append(f"<li>{_inline(item)}</li>")
            out.append("</ul>")
            continue

        # 順序付きリスト
        if re.match(r"^\s*\d+\.\s+", line):
            _flush_paragraph(paragraph)
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>")
            for item in items:
                out.append(f"<li>{_inline(item)}</li>")
            out.append("</ol>")
            continue

        # 空行 → 段落フラッシュ
        if not line.strip():
            _flush_paragraph(paragraph)
            i += 1
            continue

        # 通常テキスト
        paragraph.append(line)
        i += 1

    _flush_paragraph(paragraph)
    return "\n".join(out)


def _icon_data_uri(icon_path: Path) -> str | None:
    """アイコン画像を data URI に変換 (HTML 単体で表示できるよう埋め込み)。"""
    if not icon_path.is_file():
        return None
    mime, _ = mimetypes.guess_type(icon_path.name)
    if not mime:
        mime = "image/png"
    data = base64.b64encode(icon_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def render_page(
    title: str,
    body_html: str,
    source_path: str,
    icon_data_uri: str | None = None,
) -> str:
    if icon_data_uri:
        header = (
            f'<div class="page-header">'
            f'<img class="icon" src="{icon_data_uri}" alt="reviewer icon"/>'
            f'<div class="title-block">'
            f'<div class="source">source: {_escape(source_path)}</div>'
            f"</div>"
            f"</div>"
        )
    else:
        header = (
            f'<div class="meta">source: <code>{_escape(source_path)}</code></div>'
        )

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{_escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
{header}
{body_html}
</div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown → HTML (stdlib only)")
    parser.add_argument("input", help="Markdown ファイルのパス")
    parser.add_argument("-o", "--output", help="出力 HTML パス (省略時 _html/ 配下)")
    parser.add_argument(
        "--out-dir",
        help="出力ディレクトリ (省略時は input と同じディレクトリの _html/)",
    )
    parser.add_argument("--title", help="HTML title (省略時はファイル名)")
    parser.add_argument(
        "--icon",
        help="ヘッダー左に表示するアイコン画像のパス (省略時は .claude/assets/icon.png を自動検出)",
    )
    args = parser.parse_args()

    src = Path(args.input).resolve()
    if not src.is_file():
        print(f"[md2html] エラー: ファイルが見つかりません: {src}", file=sys.stderr)
        return 1

    md = src.read_text(encoding="utf-8")
    global _BASE_DIR
    _BASE_DIR = src.parent
    body = md_to_html(md)
    title = args.title or src.stem

    # 表示用ソースパス: プロジェクトルートからの相対
    try:
        rel_src = src.relative_to(Path.cwd())
        src_display = str(rel_src)
    except ValueError:
        src_display = str(src)

    # アイコン解決: 明示指定 > 既定パス (.claude/assets/icon.png)
    icon_uri: str | None = None
    if args.icon:
        icon_path = Path(args.icon).resolve()
        icon_uri = _icon_data_uri(icon_path)
        if icon_uri is None:
            print(
                f"[md2html] 警告: --icon で指定されたファイルが見つかりません: {icon_path}",
                file=sys.stderr,
            )
    else:
        default_icon = Path.cwd() / ".claude" / "assets" / "icon.png"
        icon_uri = _icon_data_uri(default_icon)

    page = render_page(title, body, src_display, icon_data_uri=icon_uri)

    if args.output:
        dst = Path(args.output).resolve()
    elif args.out_dir:
        dst = Path(args.out_dir).resolve() / f"{src.stem}.html"
    else:
        dst = src.parent / "_html" / f"{src.stem}.html"

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(page, encoding="utf-8")

    # 表示用に相対パス
    try:
        rel_dst = dst.relative_to(Path.cwd())
    except ValueError:
        rel_dst = dst

    print(f"[md2html] OK: {rel_dst}")
    print(f"open file://{dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
