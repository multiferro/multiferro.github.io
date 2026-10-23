# Hosting this site on GitLab Pages

The site is plain HTML, so it works on GitLab Pages without changes. The one
difference from GitHub is that GitLab publishes through a CI pipeline, which
is what `.gitlab-ci.yml` sets up: on every push to the default branch it
copies the site files into a `public/` folder and GitLab serves that.

## On gitlab.com

1. Sign in at gitlab.com. To have the site under a group name, first create a
   group (top-left "+" → "New group"), for example `multiferro`.
2. Create a blank project. The name decides the address:
   - `USERNAME.gitlab.io` (or `GROUPNAME.gitlab.io` inside a group) is served
     at `https://USERNAME.gitlab.io/`.
   - Any other name, e.g. `ferrolab`, is served at
     `https://USERNAME.gitlab.io/ferrolab/`. The site uses relative links,
     so both work.
   Set visibility to Public, and untick "Initialize repository with a README".
3. Upload the files. Either push with git from this folder:

       git init
       git add .
       git commit -m "Ferrolab website"
       git remote add origin https://gitlab.com/USERNAME/PROJECT.git
       git push -u origin main

   or use the project's "Upload file" button in the web interface for each
   file (slower; git is easier for 20 files).
4. The push starts a pipeline (left menu: Build → Pipelines). It takes about
   a minute. When it shows "passed", the site is live; the address is under
   Deploy → Pages. If "Use unique domain" is enabled there, GitLab gives a
   long random address instead: turn that option off and save to get the
   short one.

Later changes: edit, commit, push. Every push to `main` republishes.

## On a university GitLab (e.g. gitlab.YOURUNI.edu)

Same steps. The address will be whatever the instance uses for Pages, usually
`https://USERNAME.pages.YOURUNI.edu/PROJECT/`; the Pages settings page shows
it. Two things to check with IT: that Pages is enabled on the instance, and
that a shared runner is available (Settings → CI/CD → Runners), since the
pipeline needs one to run. Institutional instances sometimes require the
project to be Public (or "Internal") for Pages to be reachable from outside.

## Keeping GitHub and GitLab in sync

If you keep the GitHub site as well, push the same repository to both:

    git remote add gitlab https://gitlab.com/USERNAME/PROJECT.git
    git push gitlab main

GitLab can also mirror a GitHub repository automatically (Settings →
Repository → Mirroring repositories, direction "Pull"), so that pushing to
GitHub updates GitLab within a few minutes without a second push.

## Custom domain

Deploy → Pages → "New Domain". GitLab shows the DNS records to add at the
registrar (a CNAME or A record, plus a TXT record for verification) and
issues an HTTPS certificate automatically once they are in place.
