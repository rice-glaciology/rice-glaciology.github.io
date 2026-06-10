# Rice Glaciology — group website

Source for the [Rice Glaciology](https://rice-glaciology.github.io) group website. Built with [Hugo](https://gohugo.io/) and the [Hugo Blox](https://hugoblox.com/) research-group theme, deployed to GitHub Pages.

## Editing the site

All content lives in `content/`. The homepage is assembled from blocks in `content/_index.md` (About, Team, News, Research, Publications, Join Us).

### Add a team member (spreadsheet)

The Team section is generated from a spreadsheet, `data/team.csv`. To add someone:

1. Open `data/team.csv` in Excel, Numbers, or Google Sheets and add a row. Columns: `name, role, group, photo, website, email, github, scholar, orcid` (leave any cell blank to omit it).
2. Save/export it back as CSV.
3. Put their headshot in `assets/media/team/` (any size; it's auto-cropped to a circle) and put the filename in the `photo` column.
4. Commit and push.

People appear on the Team page in the order of the rows. On the next build, Hugo reads the CSV automatically — no other steps.

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
