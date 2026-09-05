# -*- coding: utf-8 -*-
"""
Genisys API 文档查询站 —— 动态生成服务端
------------------------------------------------------------
不预渲染任何页面。每次请求都实时读取 docs/ 下的 Markdown：
  GET /                     -> SPA 壳 (shell.html)
  GET /api/list             -> 实时扫描 docs/ 生成文档索引 JSON
  GET /api/render?file=REL  -> 实时把某篇 md 渲染成带章节锚点的 HTML
依赖：仅 Python 3 标准库。若环境已装 markdown 则优先用它；否则自动走内置纯 Python 渲染。
"""
import os
import re
import json
import html
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import markdown as _md_lib
    MARKDOWN_AVAILABLE = True
except Exception:
    _md_lib = None
    MARKDOWN_AVAILABLE = False

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.normpath(os.path.join(ROOT, "..", "docs"))
SHELL = os.path.join(ROOT, "shell.html")

VERSION_ORDER = ["0.13", "0.14.0", "0.14.3", "0.15.0", "0.16.0", "1.0.0"]
TYPE_LABEL = {"plugin": "插件 API", "core": "核心 API", "study": "关于"}


def classify(rel):
    """从相对路径推断 version / vtype。"""
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] in VERSION_ORDER and parts[0] != "study":
        name = parts[-1].lower()
        if "core" in name:
            vtype = "core"
        elif "plugin" in name:
            vtype = "plugin"
        else:
            vtype = "study"
        return parts[0], vtype
    if rel.endswith("pmmp-apidoc-study.md"):
        return "study", "study"
    return "study", "study"


def slugify(s):
    s = s.lower()
    s = re.sub(r"[`*_]", "", s)
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff\- ]", "", s)
    s = s.replace(" ", "-")
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "section"


def add_heading_ids(body_html):
    """给渲染后的 HTML 中每个 <h1>~<h6> 加唯一 id，并返回章节列表。"""
    headings = []
    seen = {}

    def repl(m):
        level = int(m.group(1))
        inner = m.group(2)
        text = re.sub(r"<[^>]+>", "", inner)
        base = slugify(text)
        if base in seen:
            seen[base] += 1
            slug = "%s-%d" % (base, seen[base])
        else:
            seen[base] = 0
            slug = base
        headings.append({"level": level, "title": text.strip(), "slug": slug})
        return '<h%d id="%s">%s</h%d>' % (level, slug, inner, level)

    out = re.sub(r"<h([1-6])>(.*?)</h\1>", repl, body_html, flags=re.S)
    return out, headings


def extract_title(raw, rel):
    for line in raw.splitlines():
        m = re.match(r"^#\s+(.*)$", line)
        if m:
            return re.sub(r"[`*]", "", m.group(1)).strip()
    return rel


def html_to_text(body_html):
    t = re.sub(r"<[^>]+>", " ", body_html)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def render_markdown(raw):
    """优先用 markdown 库；不可用时走内置纯 Python 渲染。"""
    if MARKDOWN_AVAILABLE:
        md = _md_lib.Markdown(extensions=["tables", "fenced_code"])
        return md.convert(raw)
    return _fallback_markdown(raw)


def _inline(text):
    """行内渲染：行内代码 / 链接 / 粗体 / 斜体 / 删除线。先转义再插标签。"""
    codes = []
    def stash(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)
    text = re.sub(r"`([^`]+)`", stash, text)          # 先摘出代码，避免内部被转义处理
    text = html.escape(text, quote=True)             # 转义 & < > " '
    def link(m):
        return "<a href=\"%s\">%s</a>" % (m.group(2), m.group(1))
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    def restore(m):
        return "<code>%s</code>" % html.escape(codes[int(m.group(1))], quote=False)
    text = re.sub(r"\x00(\d+)\x00", restore, text)
    return text


def _split_row(row):
    row = row.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [c.strip() for c in row.split("|")]


def _render_table(header, sep, rows):
    hs = _split_row(header)
    head = "<tr>%s</tr>" % "".join("<th>%s</th>" % _inline(h) for h in hs)
    body = []
    for r in rows:
        cs = _split_row(r)
        body.append("<tr>%s</tr>" % "".join("<td>%s</td>" % _inline(c) for c in cs))
    return "<table><thead>%s</thead><tbody>%s</tbody></table>" % (head, "".join(body))


def _is_block_start(line, nxt):
    s = line.strip()
    if s.startswith("```"):
        return True
    if re.match(r"^#{1,6}\s+", line):
        return True
    if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
        return True
    if s.startswith(">"):
        return True
    if re.match(r"^\s*([-*+]|\d+\.)\s+", line):
        return True
    if "|" in line and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", nxt) and "-" in nxt:
        return True
    return False


def _fallback_markdown(raw):
    """极简 Markdown -> HTML：标题/段落/列表/引用/代码块/表格/分割线/行内。"""
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        # 围栏代码块
        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1  # 跳过结束 ```
            cls = (' class="language-%s"' % lang) if lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (cls, html.escape("\n".join(buf), quote=False)))
            continue
        # 空行
        if not line.strip():
            i += 1; continue
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, _inline(m.group(2).strip()), lvl))
            i += 1; continue
        # 分割线
        if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
            out.append("<hr>"); i += 1; continue
        # 引用块
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].lstrip()); i += 1
            out.append("<blockquote>%s</blockquote>" % _fallback_markdown("\n".join(buf)))
            continue
        # 表格
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]) and "-" in lines[i + 1]:
            header, sep = line, lines[i + 1]
            i += 2
            rows = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                rows.append(lines[i]); i += 1
            out.append(_render_table(header, sep, rows))
            continue
        # 列表（无序/有序，单层）
        if re.match(r"^\s*([-*+]|\d+\.)\s+", line):
            items = []
            while i < n and re.match(r"^\s*([-*+]|\d+\.)\s+", lines[i]):
                content = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", lines[i])
                items.append("<li>%s</li>" % _inline(content))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue
        # 段落
        buf = [line]
        i += 1
        while i < n and lines[i].strip() and not _is_block_start(lines[i], lines[i + 1] if i + 1 < n else ""):
            buf.append(lines[i]); i += 1
        out.append("<p>%s</p>" % _inline(" ".join(s.strip() for s in buf)))
    return "\n".join(out)


def render_doc(rel):
    full = os.path.normpath(os.path.join(DOCS, rel))
    if not full.startswith(DOCS) or not rel.endswith(".md") or not os.path.isfile(full):
        return None
    raw = open(full, encoding="utf-8").read()
    body = render_markdown(raw)
    body, headings = add_heading_ids(body)
    version, vtype = classify(rel)
    return {
        "version": version,
        "vtype": vtype,
        "label": TYPE_LABEL.get(vtype, vtype),
        "title": extract_title(raw, rel),
        "file": rel,
        "headings": headings,
        "html": body,
        "search_text": html_to_text(body),
    }


def list_docs():
    out = []
    for dirpath, _, files in os.walk(DOCS):
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), DOCS).replace(os.sep, "/")
            d = render_doc(rel)
            if d:
                out.append(d)
    vidx = {v: i for i, v in enumerate(VERSION_ORDER)}
    out.sort(key=lambda d: (vidx.get(d["version"], 99), d["vtype"], d["file"]))
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # 静默

    def _send(self, data, ctype):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        if p in ("/", "/index.html"):
            try:
                self._send(open(SHELL, "rb").read(), "text/html; charset=utf-8")
            except Exception:
                self.send_error(404)
        elif p == "/api/list":
            self._send(json.dumps(list_docs(), ensure_ascii=False),
                       "application/json; charset=utf-8")
        elif p == "/api/render":
            q = urllib.parse.parse_qs(u.query)
            rel = q.get("file", [""])[0]
            if not rel:
                self.send_error(400)
                return
            d = render_doc(rel)
            if d is None:
                self.send_error(404)
                return
            self._send(json.dumps(d, ensure_ascii=False),
                       "application/json; charset=utf-8")
        else:
            self.send_error(404)


def main():
    port = int(os.environ.get("PORT", "8765"))
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("Genisys API 文档查询站已启动: http://127.0.0.1:%d/  (Ctrl+C 退出)" % port)
    print("动态渲染目录: %s" % DOCS)
    print("Markdown 渲染器: %s" % ("markdown 库" if MARKDOWN_AVAILABLE else "内置纯 Python 渲染（无需额外依赖）"))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
