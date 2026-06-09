#!/usr/bin/env python3
"""
Sync publications from Google Scholar to Hugo content/publication/.

Usage:
    python3 sync_scholar.py           # dry run (shows what would be added/skipped)
    python3 sync_scholar.py --write   # actually create files
    python3 sync_scholar.py --write --rebuild  # create files and rebuild site

Scholar rate-limits aggressive use. The script spaces requests with delays and
uses pre-filtering on citation strings to minimise the number of individual
publication fills needed.
"""

import os
import re
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path

SCHOLAR_ID = "jf4jwlMAAAAJ"
PUB_DIR = Path(__file__).parent / "content" / "publication"
DRY_RUN = "--write" not in sys.argv
REBUILD = "--rebuild" in sys.argv

# ── Venue / citation patterns that identify non-papers ─────────────────────
# These are checked against both the filled venue AND the prefilled citation string.
NON_PAPER_PATTERNS = [
    # AGU / EGU conference abstracts
    r"(?i)fall meeting",
    r"(?i)spring meeting",
    r"(?i)meeting abstract",
    r"(?i)general assembly",
    r"\bEGU\b",
    r"(?i)conference abstract",
    r"(?i)abstract volume",
    # General conference proceedings
    r"(?i)\bproceedings\b",
    r"(?i)\bsymposium\b",
    r"(?i)\bconference on\b",
    r"(?i)\bworkshop on\b",
    r"(?i)\bIEEE\b",
    r"(?i)\bSPIE\b",
    # Preprint / discussion venues
    r"(?i) discussions?$",       # "The Cryosphere Discussions"
    r"(?i)EGUsphere",
    r"(?i)authorea",
    r"(?i)essoar",
    r"(?i)arxiv",
    r"(?i)biorxiv",
    r"(?i)preprint",
    # Software / data releases
    r"(?i)^zenodo",
]


def matches_non_paper(text):
    return any(re.search(p, text) for p in NON_PAPER_PATTERNS)


def is_github_entry(pub):
    bib = pub.get("bib", {})
    title = bib.get("title", "")
    if not bib.get("pub_year", ""):
        return True
    if re.match(r"^[\w.-]+/[\w.-]+[\s:]", title):
        return True
    return False


def prefill_skip(pub):
    """Check citation/title without a fill request. Returns reason string or None."""
    bib = pub.get("bib", {})
    citation = bib.get("citation", "")
    title = bib.get("title", "")
    if matches_non_paper(citation):
        return f"citation: {citation[:60]}"
    # Titles that are clearly conference-only
    if re.search(r"(?i)\b(AGU|EGU)\b.*\b(abstract|poster|presentation)\b", title):
        return f"title pattern"
    return None


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")[:70]


def doi_to_slug(doi):
    doi = re.sub(r"^https?://doi\.org/", "", doi.strip())
    parts = doi.split("/", 1)
    return slugify(parts[1]) if len(parts) > 1 else slugify(doi)


def normalize_title(title):
    title = title.strip().lower()
    title = re.sub(r"[\u2010-\u2015\u2212\ufe58\ufe63\uff0d]", "-", title)
    title = re.sub(r"\s+", " ", title)
    return title


def get_existing_pubs():
    dois, titles = set(), set()
    for pub_path in PUB_DIR.glob("*/index.md"):
        try:
            text = pub_path.read_text()
            if text.startswith("---"):
                end = text.find("---", 3)
                if end > 0:
                    fm = yaml.safe_load(text[3:end])
                    if fm:
                        if fm.get("doi"):
                            doi = re.sub(r"^https?://doi\.org/", "", str(fm["doi"]).strip())
                            dois.add(doi.lower())
                        if fm.get("title"):
                            titles.add(normalize_title(fm["title"]))
        except Exception:
            pass
    return dois, titles


def normalize_author(name):
    name = name.strip()
    if not name:
        return name
    if "," in name:
        last, _, rest = name.partition(",")
        initials = " ".join(p[0] + "." for p in rest.strip().split() if p)
        return f"{initials} {last.strip()}" if initials else last.strip()
    return name


def extract_doi(pub_filled):
    for field in ("eprint_url", "pub_url"):
        val = pub_filled.get(field, "") or ""
        if "doi.org" in val:
            return re.sub(r"^.*doi\.org/", "", val).strip()
    return ""


def build_frontmatter(pub_filled, doi):
    bib = pub_filled.get("bib", {})
    title = bib.get("title", "Untitled")
    year = bib.get("pub_year", "")
    abstract = bib.get("abstract", "")
    journal = bib.get("journal") or bib.get("booktitle") or ""

    raw_authors = bib.get("author", "")
    if isinstance(raw_authors, str):
        author_list = [normalize_author(a.strip()) for a in raw_authors.split(" and ") if a.strip()]
    else:
        author_list = [normalize_author(str(a)) for a in (raw_authors or [])]

    date_str = f"{year}-01-01" if year else datetime.now().strftime("%Y-%m-%d")

    fm = {
        "title": title,
        "subtitle": "",
        "summary": "",
        "authors": author_list,
        "tags": [],
        "categories": [],
        "date": date_str,
        "featured": False,
        "draft": False,
        "image": {"caption": "", "focal_point": "", "preview_only": False},
        "projects": [],
        "publishDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "publication_types": ["2"],
        "abstract": abstract,
        "publication": f"*{journal}*" if journal else "",
    }
    if doi:
        fm["doi"] = doi

    return "---\n" + yaml.dump(fm, allow_unicode=True, default_flow_style=False) + "---\n"


def main():
    from scholarly import scholarly

    print(f"=== Scholar sync [{'DRY RUN' if DRY_RUN else 'WRITE'}] ===")
    print()

    try:
        author = scholarly.search_author_id(SCHOLAR_ID)
        author = scholarly.fill(author, sections=["publications"])
    except Exception as e:
        print(f"ERROR fetching author: {e}")
        print("Google Scholar is rate-limiting. Wait a few minutes and try again.")
        sys.exit(1)

    pubs = author.get("publications", [])
    print(f"Found {len(pubs)} entries on Scholar")

    existing_dois, existing_titles = get_existing_pubs()
    print(f"Found {len(list(PUB_DIR.glob('*/index.md')))} existing local publications")
    print()

    new_count = 0
    skip_existing = 0
    skip_github = 0
    skip_abstract = 0

    for i, pub in enumerate(pubs):
        bib = pub.get("bib", {})
        title = bib.get("title", "Unknown")

        # ── Pre-filter without any fill request ────────────────────────────
        if is_github_entry(pub):
            print(f"[{i+1:3d}] SKIP (github)    {title[:65]}")
            skip_github += 1
            continue

        reason = prefill_skip(pub)
        if reason:
            print(f"[{i+1:3d}] SKIP (pre-filter) {title[:55]}")
            skip_abstract += 1
            continue

        # Title/DOI already in existing set? Skip without fill.
        if normalize_title(title) in existing_titles:
            print(f"[{i+1:3d}] SKIP (exists)    {title[:65]}")
            skip_existing += 1
            continue

        # ── Need to fill to get venue and DOI ─────────────────────────────
        print(f"[{i+1:3d}] Filling:  {title[:65]}")
        pub_filled = None
        for attempt in range(3):
            try:
                pub_filled = scholarly.fill(pub)
                break
            except Exception as e:
                wait = 15 * (attempt + 1)
                print(f"      retry {attempt+1}/3 after {wait}s ({e})")
                time.sleep(wait)

        if pub_filled is None:
            print(f"      SKIP (fetch failed after retries)")
            continue

        # Post-fill venue check
        bib_f = pub_filled.get("bib", {})
        journal = (bib_f.get("journal") or "").strip()
        booktitle = (bib_f.get("booktitle") or "").strip()
        venue = (journal or booktitle).strip()

        # If venue comes from booktitle (not journal), it's a conference paper
        if booktitle and not journal:
            print(f"      SKIP (conference proceedings) venue: {booktitle[:60]}")
            skip_abstract += 1
            time.sleep(1)
            continue

        if matches_non_paper(venue):
            print(f"      SKIP (not paper) venue: {venue}")
            skip_abstract += 1
            time.sleep(1)
            continue

        # Blank venue + no DOI = ambiguous; skip
        doi = extract_doi(pub_filled)
        if not venue and not doi:
            print(f"      SKIP (no venue/doi)")
            skip_abstract += 1
            time.sleep(1)
            continue

        title_clean = bib_f.get("title", title).strip()

        # Title duplicate check (after fill, in case title changed)
        if normalize_title(title_clean) in existing_titles:
            print(f"      SKIP (exists) title match after fill")
            skip_existing += 1
            time.sleep(1)
            continue

        if doi and doi.lower() in existing_dois:
            print(f"      SKIP (exists) doi match")
            skip_existing += 1
            time.sleep(1)
            continue

        # ── Generate slug ─────────────────────────────────────────────────
        slug = doi_to_slug(doi) if doi else slugify(title_clean)
        if not slug:
            print(f"      SKIP (no slug)")
            continue

        pub_path = PUB_DIR / slug
        if pub_path.exists():
            print(f"      SKIP (dir exists) {slug}")
            skip_existing += 1
            time.sleep(1)
            continue

        year = bib_f.get("pub_year", "")
        print(f"      NEW  ({year}) {venue[:50]}")

        if not DRY_RUN:
            content = build_frontmatter(pub_filled, doi)
            pub_path.mkdir(parents=True, exist_ok=True)
            (pub_path / "index.md").write_text(content)

        new_count += 1
        time.sleep(3)  # polite delay between fills

    print()
    print(f"Results: {new_count} new  |  {skip_existing} already exist  "
          f"|  {skip_abstract} filtered (abstracts/preprints)  |  {skip_github} github")

    if not DRY_RUN and new_count > 0 and REBUILD:
        print("\nRebuilding site...")
        os.system("hugo --gc --minify")
    elif DRY_RUN and new_count > 0:
        print(f"\nRun with --write to create {new_count} new publication files.")
        print("Add --rebuild to also regenerate the site.")


if __name__ == "__main__":
    main()
