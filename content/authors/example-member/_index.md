---
# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE — how to add a group member.
#
# 1. Copy this folder: content/authors/example-member  →  content/authors/firstname-lastname
# 2. Edit the fields below.
# 3. Add a square photo named `avatar.jpg` (or .png) inside the new folder.
# 4. Set `draft: false` so the person appears on the site.
#
# `user_groups` controls which Team section the person shows up under on the
# homepage. Use one of these EXACT values (defined in content/_index.md):
#   Principal Investigators · Postdoctoral Researchers · Graduate Students
#   Undergraduate Students · Research Staff · Alumni
# ─────────────────────────────────────────────────────────────────────────────

# Keep as a draft until filled in (draft authors are not published).
draft: true

# Display name
title: "First Last"
first_name: First
last_name: Last

superuser: false

# Role/position (shown under the name)
role: "PhD Student"

# Team section(s) this person belongs to
user_groups:
  - Graduate Students

# Square photo placed in this folder, e.g. avatar.jpg
avatar: avatar.jpg

organizations:
  - name: Rice University
    url: 'https://www.rice.edu/'

bio: One or two sentences about research interests.

interests:
  - Glaciology
  - Remote Sensing

education:
  courses:
    - course: BS in Geophysics
      institution: Some University
      year: 2024

# Social / academic links. Remove any you don't need.
# Icons: https://docs.hugoblox.com/getting-started/page-builder/#icons
social:
  - icon: envelope
    icon_pack: fas
    link: 'mailto:netid@rice.edu'
  - icon: github
    icon_pack: fab
    link: https://github.com/username
  - icon: google-scholar
    icon_pack: ai
    link: https://scholar.google.com/citations?user=XXXXXXXX
  - icon: orcid
    icon_pack: ai
    link: https://orcid.org/0000-0000-0000-0000

highlight_name: false
summary: "Short one-line summary."
---
