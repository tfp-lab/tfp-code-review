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
:root {
  --fg: #24292f;
  --fg-strong: #0d1117;
  --muted: #656d76;
  --bg: #ffffff;
  --bg-soft: #f6f8fa;
  --code-bg: #f6f8fa;
  --code-fg: #24292f;
  --border: #d0d7de;
  --border-soft: #eaeef2;
  --link: #0969da;
  --link-hover: #0550ae;
  --accent: #0969da;
  --accent-soft: #ddf4ff;
  --warn-bg: #fff8c5;
  --warn-border: #d4a72c;
  --shadow: 0 1px 3px rgba(31, 35, 40, 0.08), 0 1px 2px rgba(31, 35, 40, 0.04);
}
@media (prefers-color-scheme: dark) {
  :root {
    --fg: #c9d1d9;
    --fg-strong: #f0f6fc;
    --muted: #8b949e;
    --bg: #0d1117;
    --bg-soft: #161b22;
    --code-bg: #161b22;
    --code-fg: #c9d1d9;
    --border: #30363d;
    --border-soft: #21262d;
    --link: #58a6ff;
    --link-hover: #79c0ff;
    --accent: #58a6ff;
    --accent-soft: #0c2d6b;
    --warn-bg: #341a00;
    --warn-border: #9e6a03;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  }
}

* { box-sizing: border-box; }
html { font-size: 16px; scroll-behavior: smooth; }
body {
  margin: 0;
  padding: 0;
  color: var(--fg);
  background: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans",
               "Hiragino Kaku Gothic ProN", "Noto Sans JP", "Yu Gothic",
               "Segoe UI", Roboto, sans-serif;
  font-feature-settings: "palt" 1;
  line-height: 1.85;
  letter-spacing: 0.02em;
  word-wrap: break-word;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.container {
  max-width: 880px;
  margin: 0 auto;
  padding: 3rem 1.75rem 6rem;
}

/* === Headings === */
h1, h2, h3, h4, h5, h6 {
  color: var(--fg-strong);
  line-height: 1.35;
  font-weight: 700;
  letter-spacing: -0.01em;
}
h1 {
  font-size: 2.2rem;
  margin: 0 0 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--border);
}
h2 {
  font-size: 1.55rem;
  margin: 3rem 0 1rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--border-soft);
  position: relative;
}
h2::before {
  content: "";
  position: absolute;
  left: -1rem;
  top: 0.4em;
  width: 4px;
  height: 1.1em;
  background: var(--accent);
  border-radius: 2px;
}
h3 {
  font-size: 1.25rem;
  margin: 2rem 0 0.7rem;
}
h4 {
  font-size: 1.08rem;
  margin: 1.5rem 0 0.5rem;
  color: var(--fg);
}
h5, h6 { font-size: 1rem; margin: 1.2rem 0 0.4rem; }

/* === Body text === */
p { margin: 0.85rem 0; }
strong { color: var(--fg-strong); font-weight: 700; }
em { font-style: italic; color: var(--fg-strong); }

a {
  color: var(--link);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}
a:hover {
  color: var(--link-hover);
  border-bottom-color: var(--link-hover);
}

/* === Code === */
code {
  font-family: "SFMono-Regular", "JetBrains Mono", Consolas,
               "Liberation Mono", Menlo, monospace;
  font-size: 0.88em;
  background: var(--bg-soft);
  color: var(--code-fg);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  border: 1px solid var(--border-soft);
}
pre {
  background: var(--code-bg);
  padding: 1.1rem 1.25rem;
  border-radius: 8px;
  overflow-x: auto;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  margin: 1.2rem 0;
  font-size: 0.92rem;
  line-height: 1.6;
}
pre code {
  background: transparent;
  border: none;
  padding: 0;
  font-size: inherit;
  color: inherit;
}

/* === Quote === */
blockquote {
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  padding: 0.6rem 1.1rem;
  margin: 1.2rem 0;
  border-radius: 0 6px 6px 0;
  color: var(--fg);
}
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }

/* === Lists === */
ul, ol {
  padding-left: 1.7rem;
  margin: 0.7rem 0;
}
li { margin: 0.35rem 0; }
li > ul, li > ol { margin: 0.3rem 0; }

/* チェックボックス (タスクリスト) */
li input[type="checkbox"] {
  margin-right: 0.4rem;
  transform: translateY(1px);
  accent-color: var(--accent);
}

/* === HR === */
hr {
  border: none;
  border-top: 1px solid var(--border-soft);
  margin: 2.5rem 0;
}

/* === Tables === */
table {
  border-collapse: collapse;
  margin: 1.3rem 0;
  display: block;
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  font-size: 0.95rem;
}
thead {
  background: var(--bg-soft);
}
th, td {
  border: none;
  border-bottom: 1px solid var(--border-soft);
  padding: 0.65rem 1rem;
  text-align: left;
  vertical-align: top;
}
th {
  font-weight: 700;
  color: var(--fg-strong);
  border-bottom: 2px solid var(--border);
  white-space: nowrap;
}
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: var(--bg-soft); }

/* === Page header with icon === */
.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 0 0 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-soft);
}
.page-header .icon {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: 12px;
  background: var(--bg-soft);
  border: 1px solid var(--border);
  padding: 4px;
  image-rendering: pixelated;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
}
.page-header .title-block {
  flex: 1;
  min-width: 0;
}
.page-header .title-block .source {
  font-size: 0.78rem;
  color: var(--muted);
  font-family: "SFMono-Regular", Consolas, monospace;
  word-break: break-all;
}

/* === Meta header === */
.meta {
  color: var(--muted);
  font-size: 0.82rem;
  margin: 0 0 2rem;
  padding: 0.6rem 0.9rem;
  background: var(--bg-soft);
  border-left: 3px solid var(--accent);
  border-radius: 0 4px 4px 0;
}
.meta code {
  background: transparent;
  border: none;
  padding: 0;
  font-size: 0.95em;
  color: var(--muted);
}

/* === Mobile === */
@media (max-width: 640px) {
  .container { padding: 1.5rem 1rem 4rem; }
  h1 { font-size: 1.7rem; }
  h2 { font-size: 1.3rem; }
  h2::before { display: none; }
  h3 { font-size: 1.1rem; }
  pre { font-size: 0.85rem; padding: 0.9rem; }
  table { font-size: 0.88rem; }
  th, td { padding: 0.5rem 0.7rem; }
}

/* === Print === */
@media print {
  body { background: #fff; color: #000; }
  .container { max-width: none; padding: 0; }
  pre, blockquote, table { box-shadow: none; }
  a { color: #000; border-bottom-color: #999; }
  h2::before { display: none; }
}
"""


def _escape(s: str) -> str:
    return html.escape(s, quote=False)


def _inline(text: str) -> str:
    """インライン記法 (コード/強調/リンク) を HTML に変換。"""
    # 1) インラインコードを先に退避 (中身のエスケープを保護)
    placeholders: list[str] = []

    def _save_code(m: re.Match) -> str:
        placeholders.append(f"<code>{_escape(m.group(1))}</code>")
        return f"\x00CODE{len(placeholders) - 1}\x00"

    text = re.sub(r"`([^`]+)`", _save_code, text)

    # 2) 残りをエスケープ
    text = _escape(text)

    # 3) リンク [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        text,
    )

    # 4) 強調 (** > * の順)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\s][^*]*?)\*(?!\*)", r"<em>\1</em>", text)

    # 5) コードプレースホルダ復元
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
