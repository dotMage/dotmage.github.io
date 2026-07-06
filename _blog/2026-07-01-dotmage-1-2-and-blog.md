---
title: dotMage 1.2 — and a blog to announce it on
title_ru: dotMage 1.2 — и блог, где об этом рассказать
tag: release
summary: App deletion, folders, smarter update checks — and this blog, where every release gets proper notes from now on.
summary_ru: Удаление приложений, папки, умная проверка обновлений — и этот блог, где у каждого релиза теперь будут нормальные заметки.
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
<!-- ru -->

dotMage тихо выкатывал фичи с июня — папки, CI-токены, веб-админка, жизненный цикл
приложений. «Тихо» — это и есть проблема: заметки о релизах жили в сообщениях коммитов.
С этого момента каждый релиз публикуется здесь: человеческое резюме сверху, полный
чейнджлог ниже.

## Что нового в 1.2

### Удаление приложений

Приложения больше не навсегда:

```
$ dmage app rm old-project
This will delete 'old-project' and ALL its environments. Type 'old-project' to confirm:
```

### Умная проверка обновлений

Баннер проверяет GitHub на новые релизы (кэш на 24 часа) и сравнивает версии по
правилам semver — `1.10.0` новее, чем `1.9.0`.

## Чейнджлог

### 1.2.1

#### Исправлено
- Проверка обновлений сравнивает версии по правилам semver.

### 1.2.0

#### Добавлено
- `dmage app rm` — удаление приложения со всеми его окружениями.

## Скачать

Бинарники: [github.com/dotMage/dotmage/releases](https://github.com/dotMage/dotmage/releases)

```
brew upgrade dotmage
```
