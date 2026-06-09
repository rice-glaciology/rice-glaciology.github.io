# Rice Glaciology — group website

Source for the [Rice Glaciology](https://rice-glaciology.github.io) group website. Built with [Hugo](https://gohugo.io/) and the [Hugo Blox](https://hugoblox.com/) research-group theme, deployed to GitHub Pages.

## Editing the site

All content lives in `content/`. The homepage is assembled from blocks in `content/_index.md` (About, Team, News, Research, Publications, Join Us).

### Add a team member

1. Copy `content/authors/example-member/` to `content/authors/firstname-lastname/`.
2. Edit `_index.md` (name, role, links). Put a square photo named `avatar.jpg` in the folder.
3. Set `user_groups` to one of: `Principal Investigators`, `Postdoctoral Researchers`, `Graduate Students`, `Undergraduate Students`, `Research Staff`, `Alumni`.
4. Set `draft: false` so the person is published.

The order of groups on the Team section is set by `user_groups` in `content/_index.md`.

### Post group news

Create `content/post/YYYY-MM-DD-short-title/index.md`:

```markdown
---
title: A short, clear headline
date: 2026-06-09
authors:
  - andrew_hoffman
tags:
  - Group
---

Your news text here. An optional image named `featured.jpg` in the same folder
will be used as the thumbnail.
```

The newest posts appear on the homepage News section; the full archive is at `/post/`.

### Publications

Publication entries live in `content/publication/`. They can be synced from Google Scholar with `sync_scholar.py` and the workflows in `.github/workflows/`. The homepage shows the most recent few; the full list links to Google Scholar.

## Run locally

Requires Hugo **extended** (matching the version in `.github/workflows/publish.yaml`):

```bash
hugo server
```

Then open http://localhost:1313.

## Deploy

Pushing to `main` triggers `.github/workflows/publish.yaml`, which builds the site and deploys it to GitHub Pages. In the repository **Settings → Pages**, set **Source** to **GitHub Actions**.
