# Blog sources

Each post is one Markdown file named `YYYY-MM-DD-slug.md`, **bilingual** (EN + RU):

```
---
title: dotMage 1.3.0 released
title_ru: Вышел dotMage 1.3.0
tag: release            # release | engineering
summary: One sentence for the post list, meta description, and Atom feed.
summary_ru: Одно предложение для списка, meta description и Atom-ленты.
---
English body...
<!-- ru -->
Русский текст...
```

Published URLs: `https://dotmage.github.io/blog/YYYY/slug/` (EN) and
`https://dotmage.github.io/blog/ru/YYYY/slug/` (RU). The language toggle in the blog
header shares `localStorage["dm_lang"]` with the landing and docs, so the choice follows
the reader across the site. Missing `title_ru`/`summary_ru`/`<!-- ru -->` fall back to
English — an EN-only post still gets a working RU page.

For release posts, start from `_post-template.md` (see the release runbook in the
private `dotmage-spec` repo).

## Build & preview

```bash
pip install markdown
python3 scripts/build_blog.py
open blog/index.html
```

Regenerates `blog/` + `blog/ru/` (post pages + indexes), both Atom feeds, and `sitemap.xml` from scratch —
deterministic, safe to re-run. CI runs the same script on every push that touches `_blog/`
and commits the output, so committing generated files locally is optional.

Markdown supports fenced code blocks and tables. Images: put files next to the sources is
NOT supported — use absolute paths to files committed elsewhere in the site.
