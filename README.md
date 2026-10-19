# Ferrolab website

Static site for Sergey Lisenkov's research group, Department of Physics,
University of South Florida. Plain HTML and CSS, no build system, so it works
on GitHub Pages (or any web server) as soon as the files are pushed.

## Files

| File | What it is |
|---|---|
| `index.html` | Home: portrait, bio, research summary, recent papers, contact |
| `research.html` | Research topics with representative papers |
| `publications.html` | **Generated** from `publications.bib` (see below) |
| `teaching.html` | Courses taught |
| `funding.html` | Grants |
| `style.css` | All styling; colours and fonts are set at the top |
| `publications.bib` | The publication list, one BibTeX entry per paper |
| `tools/make_publications.py` | Rebuilds `publications.html` and the recent-papers block on the home page |
| `tools/publications_template.html` | Page frame used by the script (text above the list lives here) |
| `assets/photo.jpg` | Portrait. Replace this file with your photo (same name); 4:5 aspect ratio fits best |
| `assets/favicon.svg` | Browser-tab icon |
| `Lisenkov-CV.pdf` | The CV linked from the navigation; replace when you update it |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |

## Putting it on GitHub Pages

1. Create a new repository on GitHub. For the address `USERNAME.github.io`
   name the repository exactly `USERNAME.github.io`; any other name gives
   `USERNAME.github.io/REPONAME/` (both work, the site uses relative links).
   To host it under an organization, create the organization first and make
   the repository there.
2. Upload these files to the repository (drag and drop on the GitHub page, or
   `git init`, `git add .`, `git commit`, `git push` from this folder).
3. In the repository go to Settings, then Pages, and under "Build and
   deployment" choose Source: "Deploy from a branch", Branch: `main`, folder
   `/ (root)`. Save.
4. After a minute the site is live at the address shown on that page.
   Every later push updates it automatically.

A custom domain (for example `ferrolab.org`) can be added on the same
settings page once you own one.

## Adding a paper

1. Add an entry to `publications.bib`, anywhere; entries are sorted by year
   automatically (newest first) and keep file order within a year, so put a
   new paper above older ones from the same year. Example:

   ```bibtex
   @article{lisenkov2027example,
     author  = {A. Author and Sergey Lisenkov and I. Ponomareva},
     title   = {Title with formulas such as PbZrO$_3$ and Ba(Ti$_{1-x}$,Zr$_x$)O$_3$},
     journal = {Physical Review B},
     volume  = {115},
     pages   = {014101},
     year    = {2027},
     doi     = {10.1103/PhysRevB.115.014101},
     arxiv   = {2612.01234}
   }
   ```

   `doi` is preferred for the title link; use `url = {...}` when there is
   no DOI. `arxiv` adds a small arXiv link. Any name containing "Lisenkov"
   is printed in bold.

2. Run, from this folder:

   ```
   python3 tools/make_publications.py
   ```

   This rewrites `publications.html` and the five most recent papers on
   `index.html`. Nothing to install; it only needs Python 3.

3. Update the counts in the summary sentence at the top of
   `tools/publications_template.html` if the paper is in one of the journals
   listed there, then run the script again.

4. Commit and push.

## Editing other pages

Open the `.html` file and edit the text. Each page repeats the same header
and footer; if you add a page, copy the header block from an existing one
and move `aria-current="page"` to the new page's link.

Each topic on `research.html` has a drawn schematic inside
`<figure class="theme-fig">`. To use a figure from one of your papers instead,
put the image in `assets/` and replace the `<svg>...</svg>` block with
`<img src="assets/yourfigure.png" alt="what it shows">`, keeping the caption.

Colours live in the `:root` block at the top of `style.css` (`--green` is
USF green). The "Updated" date is in the footer of every page.
