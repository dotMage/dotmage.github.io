---
title: dotMage 1.2 — and a blog to announce it on
tag: release
summary: App deletion, folders, smarter update checks — and this blog, where every release gets proper notes from now on.
---

dotMage has been shipping quietly since June — folders, CI tokens, a web admin, an app
lifecycle. Quietly is the problem: release notes lived in commit messages. From now on
every release lands here, with a human summary on top and the full changelog below.

## What's new in 1.2

### Delete apps

Apps are no longer forever:

```
$ dmage app rm old-project
This will delete 'old-project' and ALL its environments. Type 'old-project' to confirm:
```

### Smarter update checks

The banner checks GitHub for new releases (cached for 24h) and compares versions with
proper semver ordering — `1.10.0` is newer than `1.9.0`.

## Changelog

### 1.2.1

#### Fixed
- Update checker compares versions with proper semver ordering.

### 1.2.0

#### Added
- `dmage app rm` — delete an application and all its environments.

## Downloads

Binaries: [github.com/dotMage/dotmage/releases](https://github.com/dotMage/dotmage/releases)

```
brew upgrade dotmage
```
