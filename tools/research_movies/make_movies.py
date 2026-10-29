"""Render the short movies shown beside each area on the Research page.

Run from the repository root:

    python tools/research_movies/make_movies.py                 # all movies
    python tools/research_movies/make_movies.py firn ice-flow   # some of them
    python tools/research_movies/make_movies.py --preview 0.5 --out /tmp/p   # stills only
    python tools/research_movies/make_movies.py --list

Needs numpy, scipy, matplotlib and ffmpeg on the PATH. Writes an MP4 and a
poster JPEG per movie to static/media/research/.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # noqa: E402
import firn  # noqa: E402,F401  (each module registers its movie)
import ice_flow  # noqa: E402,F401
import radar  # noqa: E402,F401
import shelf_melt  # noqa: E402,F401
import subsidence  # noqa: E402,F401


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slugs", nargs="*", help="movies to render (default: all)")
    p.add_argument("--preview", type=float, metavar="T",
                   help="write one still at normalized time T instead of a movie")
    p.add_argument("--list", action="store_true")
    p.add_argument("--out", default=common.OUT_DIR)
    a = p.parse_args()
    ordered = sorted(common.MOVIES, key=lambda s: common.MOVIES[s]["order"])
    if a.list:
        print("\n".join(ordered))
        return
    unknown = set(a.slugs) - set(common.MOVIES)
    if unknown:
        p.error(f"unknown movie(s): {', '.join(sorted(unknown))}")
    for slug in ordered:
        if a.slugs and slug not in a.slugs:
            continue
        t0 = time.time()
        path = common.render(slug, out_dir=a.out, preview_at=a.preview)
        print(f"{slug:12s} {time.time() - t0:6.1f} s  ->  {os.path.relpath(path)}", flush=True)


if __name__ == "__main__":
    main()
