# portfolio

Portfolio of Vasili Holub, Senior .NET Developer. Live at https://vasili.holub.poly-mind.net

- `index.html` is the whole site: nine 1440×900 pages, fonts embedded, no external resources.
- `design/` holds the nine design artboards the site is built from (export of a visual design tool; only the `.dc.html` files are kept).
- `build.py` assembles `index.html` from `design/`, takes the full case stories and the fonts from the job search kit next to this repo, replaces the e-mail and fixes the three pages that ran past the 900px canvas. Run from this folder: `python3 build.py`.
