#!/usr/bin/env python3
"""Build the dotMage blog (bilingual): _blog/*.md -> blog/... (en) + blog/ru/... (ru).

Post source format — one file, both languages:

    ---
    title: dotMage 1.3.0 released
    title_ru: Вышел dotMage 1.3.0
    tag: release
    summary: One sentence for lists and feeds.
    summary_ru: Одно предложение для списков и лент.
    ---
    English body...
    <!-- ru -->
    Русский текст...

Missing *_ru fields / missing `<!-- ru -->` section fall back to English, so an
EN-only post still gets a /blog/ru/ page (no broken toggles).

Deterministic and idempotent. Usage: python3 scripts/build_blog.py
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
RU_SPLIT = "<!-- ru -->"

POST_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

RU_MONTHS = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]

STRINGS = {
    "en": {
        "index_title": "Blog — dotMage",
        "index_desc": "Release announcements and engineering notes from the dotMage project.",
        "head_h1": "Release notes &amp; engineering",
        "head_sub": "Announcements, changelogs, and how dotMage works under the hood.",
        "feed_label": "Atom feed",
        "back": "◂ All posts",
        "tagline": "dotMage — E2E-encrypted .env manager",
        "feed_title": "dotMage blog",
    },
    "ru": {
        "index_title": "Блог — dotMage",
        "index_desc": "Анонсы релизов и инженерные заметки проекта dotMage.",
        "head_h1": "Релизы и инженерные заметки",
        "head_sub": "Анонсы, чейнджлоги и то, как dotMage устроен под капотом.",
        "feed_label": "Atom-лента",
        "back": "◂ Все посты",
        "tagline": "dotMage — E2E-шифрованный менеджер .env",
        "feed_title": "Блог dotMage",
    },
}


def md_render(text: str) -> str:
    return markdown.markdown(
        text, extensions=["fenced_code", "tables"], output_format="html5"
    )


def date_human(d: date, lang: str) -> str:
    if lang == "ru":
        return f"{d.day} {RU_MONTHS[d.month - 1]} {d.year}"
    return d.strftime("%B %-d, %Y")


def blog_root(lang: str) -> str:
    return "blog/" if lang == "en" else "blog/ru/"


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
    if RU_SPLIT in body:
        body_en, body_ru = body.split(RU_SPLIT, 1)
    else:
        body_en, body_ru = body, body  # EN-only post: ru page mirrors en

    d = date(int(year), int(month), int(day))
    return {
        "slug": slug,
        "year": year,
        "date": d,
        "tag": meta["tag"],
        "en": {
            "title": meta["title"],
            "summary": meta["summary"],
            "content": md_render(body_en),
            "url": f"blog/{year}/{slug}/",
        },
        "ru": {
            "title": meta.get("title_ru") or meta["title"],
            "summary": meta.get("summary_ru") or meta["summary"],
            "content": md_render(body_ru),
            "url": f"blog/ru/{year}/{slug}/",
        },
    }


def render(template: str, mapping: dict) -> str:
    for key, value in mapping.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def lang_mapping(lang: str, p: dict | None = None) -> dict:
    """Common template vars: language, toggle URLs, UI strings."""
    t = STRINGS[lang]
    if p:
        en_url, ru_url = "/" + p["en"]["url"], "/" + p["ru"]["url"]
    else:
        en_url, ru_url = "/blog/", "/blog/ru/"
    return {
        "lang": lang,
        "en_url": en_url,
        "ru_url": ru_url,
        "en_on": "on" if lang == "en" else "",
        "ru_on": "on" if lang == "ru" else "",
        "feed_url": "/" + blog_root(lang) + "atom.xml",
        "blog_index_url": "/" + blog_root(lang),
        **{f"t_{k}": v for k, v in t.items()},
    }


def atom_entry(p: dict, lang: str) -> str:
    loc = p[lang]
    updated = f"{p['date'].isoformat()}T00:00:00Z"
    return f"""  <entry>
    <title>{html.escape(loc['title'])}</title>
    <link href="{SITE}/{loc['url']}"/>
    <id>{SITE}/{loc['url']}</id>
    <updated>{updated}</updated>
    <summary>{html.escape(loc['summary'])}</summary>
    <category term="{html.escape(p['tag'])}"/>
  </entry>"""


def write_feed(posts: list, lang: str) -> None:
    t = STRINGS[lang]
    root = blog_root(lang)
    feed_updated = (
        f"{posts[0]['date'].isoformat()}T00:00:00Z"
        if posts
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    )
    entries = "\n".join(atom_entry(p, lang) for p in posts)
    dest = ROOT / root / "atom.xml"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{lang}">
  <title>{t['feed_title']}</title>
  <link href="{SITE}/{root}"/>
  <link rel="self" href="{SITE}/{root}atom.xml"/>
  <id>{SITE}/{root}</id>
  <updated>{feed_updated}</updated>
{entries}
</feed>
""",
        encoding="utf-8",
    )


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

    for lang in ("en", "ru"):
        for p in posts:
            loc = p[lang]
            page = render(post_tpl, {
                **lang_mapping(lang, p),
                "title": html.escape(loc["title"]),
                "summary": html.escape(loc["summary"]),
                "tag": html.escape(p["tag"]),
                "date_human": date_human(p["date"], lang),
                "url": loc["url"],
                "alt_en": SITE + "/" + p["en"]["url"],
                "alt_ru": SITE + "/" + p["ru"]["url"],
                "content": loc["content"],
            })
            dest = ROOT / loc["url"] / "index.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page, encoding="utf-8")

        cards = "\n".join(
            f'''<a class="postcard" href="/{p[lang]['url']}">
  <div class="meta"><span class="tag">{html.escape(p['tag'])}</span><span>{date_human(p['date'], lang)}</span></div>
  <h2>{html.escape(p[lang]['title'])}</h2>
  <p>{html.escape(p[lang]['summary'])}</p>
</a>'''
            for p in posts
        )
        index_page = render(index_tpl, {
            **lang_mapping(lang),
            "alt_en": SITE + "/blog/",
            "alt_ru": SITE + "/blog/ru/",
            "posts": cards,
        })
        dest = ROOT / blog_root(lang) / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(index_page, encoding="utf-8")

        write_feed(posts, lang)

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + sitemap_url(f"{SITE}/", "1.0")
        + sitemap_url(f"{SITE}/docs/", "0.8")
        + sitemap_url(f"{SITE}/blog/", "0.8")
        + sitemap_url(f"{SITE}/blog/ru/", "0.8")
        + "".join(
            sitemap_url(f"{SITE}/{p[lang]['url']}", "0.6")
            for p in posts
            for lang in ("en", "ru")
        )
        + "</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    print(f"built {len(posts)} post(s) × 2 languages -> blog/, blog/ru/, feeds, sitemap.xml")


if __name__ == "__main__":
    main()
