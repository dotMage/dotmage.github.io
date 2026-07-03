#!/usr/bin/env python3
"""Build the dotMage blog: _blog/*.md -> blog/YYYY/slug/index.html + index + atom.xml.

Deterministic and idempotent: output depends only on the sources.
Usage: python3 scripts/build_blog.py   (from the repo root; needs `pip install markdown`)
"""

import re
import sys
import html
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("error: pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_blog"
OUT = ROOT / "blog"
SITE = "https://dotmage.github.io"

POST_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def parse_post(path: Path) -> dict:
    m = POST_RE.match(path.name)
    if not m:
        # Digit-prefixed but malformed = probably a typo in a post name — fail loudly.
        sys.exit(f"error: {path.name}: expected YYYY-MM-DD-slug.md")
    year, month, day, slug = m.groups()

    text = path.read_text(encoding="utf-8")
    fm = FM_RE.match(text)
    if not fm:
        sys.exit(f"error: {path.name}: missing front matter (--- title/tag/summary ---)")

    meta = {}
    for line in fm.group(1).splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    for required in ("title", "tag", "summary"):
        if not meta.get(required):
            sys.exit(f"error: {path.name}: front matter missing '{required}'")

    body = text[fm.end():]
    content = markdown.markdown(
        body, extensions=["fenced_code", "tables"], output_format="html5"
    )

    d = date(int(year), int(month), int(day))
    return {
        "slug": slug,
        "date": d,
        "url": f"blog/{year}/{slug}/",
        "title": meta["title"],
        "tag": meta["tag"],
        "summary": meta["summary"],
        "content": content,
    }


def render(template: str, mapping: dict) -> str:
    for key, value in mapping.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def atom_entry(p: dict) -> str:
    updated = f"{p['date'].isoformat()}T00:00:00Z"
    return f"""  <entry>
    <title>{html.escape(p['title'])}</title>
    <link href="{SITE}/{p['url']}"/>
    <id>{SITE}/{p['url']}</id>
    <updated>{updated}</updated>
    <summary>{html.escape(p['summary'])}</summary>
    <category term="{html.escape(p['tag'])}"/>
  </entry>"""


def sitemap_url(loc: str, priority: str) -> str:
    return (
        "  <url>\n"
        f"    <loc>{loc}</loc>\n"
        "    <changefreq>weekly</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>\n"
    )


def main() -> None:
    post_tpl = (SRC / "_template.html").read_text(encoding="utf-8")
    index_tpl = (SRC / "_index-template.html").read_text(encoding="utf-8")

    posts = sorted(
        (parse_post(p) for p in SRC.glob("*.md") if p.name[:1].isdigit()),
        key=lambda p: (p["date"], p["slug"]),
        reverse=True,
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for p in posts:
        page = render(post_tpl, {
            "title": html.escape(p["title"]),
            "summary": html.escape(p["summary"]),
            "tag": html.escape(p["tag"]),
            "date_human": p["date"].strftime("%B %-d, %Y"),
            "url": p["url"],
            "content": p["content"],
        })
        dest = ROOT / p["url"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")

    cards = "\n".join(
        f'''<a class="postcard" href="/{p['url']}">
  <div class="meta"><span class="tag">{html.escape(p['tag'])}</span><span>{p['date'].strftime('%B %-d, %Y')}</span></div>
  <h2>{html.escape(p['title'])}</h2>
  <p>{html.escape(p['summary'])}</p>
</a>'''
        for p in posts
    )
    (OUT / "index.html").write_text(
        render(index_tpl, {"posts": cards}), encoding="utf-8"
    )

    feed_updated = (
        f"{posts[0]['date'].isoformat()}T00:00:00Z"
        if posts
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    )
    entries = "\n".join(atom_entry(p) for p in posts)
    (OUT / "atom.xml").write_text(
        f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>dotMage blog</title>
  <link href="{SITE}/blog/"/>
  <link rel="self" href="{SITE}/blog/atom.xml"/>
  <id>{SITE}/blog/</id>
  <updated>{feed_updated}</updated>
{entries}
</feed>
""",
        encoding="utf-8",
    )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + sitemap_url(f"{SITE}/", "1.0")
        + sitemap_url(f"{SITE}/docs/", "0.8")
        + sitemap_url(f"{SITE}/blog/", "0.8")
        + "".join(sitemap_url(f"{SITE}/{p['url']}", "0.6") for p in posts)
        + "</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    print(f"built {len(posts)} post(s) -> blog/, atom.xml, sitemap.xml")


if __name__ == "__main__":
    main()
