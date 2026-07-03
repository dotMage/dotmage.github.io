# Blog sources

Each post is one Markdown file named `YYYY-MM-DD-slug.md` with front matter:

```
---
title: dotMage 1.3.0 released
tag: release            # release | engineering
summary: One sentence for the post list, meta description, and Atom feed.
---
```

The published URL is `https://dotmage.github.io/blog/YYYY/slug/`.

For release posts, start from `_post-template.md` (see
[dotmage-spec/RELEASING.md](https://github.com/dotMage/dotmage-spec/blob/main/RELEASING.md)).

## Build & preview

```bash
pip install markdown
python3 scripts/build_blog.py
open blog/index.html
```

Regenerates `blog/` (post pages + index), `blog/atom.xml`, and `sitemap.xml` from scratch —
deterministic, safe to re-run. CI runs the same script on every push that touches `_blog/`
and commits the output, so committing generated files locally is optional.

Markdown supports fenced code blocks and tables. Images: put files next to the sources is
NOT supported — use absolute paths to files committed elsewhere in the site.
