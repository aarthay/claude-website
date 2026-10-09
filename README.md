# Antonio Arthay, P.E. | Engineered Structural Sculptures

The website for Engineered Structural Sculptures, LLC: a full-width gallery of
drawings, plus pages for Designs, Models, Sculptures, About and Contact. It is a
static site built with [Jekyll](https://jekyllrb.com/) and published free on
GitHub Pages. The **Login** link opens an admin area where you add artwork and
edit text in the browser. Each save publishes the site again within a couple
of minutes.

## One-time setup

1. **Make `main` the default branch.** In this repository on GitHub, go to
   **Settings → General → Default branch** and make sure it is `main`. (If the
   default is another branch, rename that branch to `main` from
   **Settings → Branches**.)
2. **Turn on GitHub Pages.** Go to **Settings → Pages → Build and deployment**
   and set **Source** to **GitHub Actions**. The site then publishes on every
   change to `main`, at <https://aarthay.github.io/claude-website/>.
3. **Create your admin key** (a GitHub *personal access token*):
   1. Open <https://github.com/settings/personal-access-tokens/new>.
   2. Name it something like "Website admin" and pick an expiry date. GitHub
      will email you before it expires; make a new one the same way.
   3. Under **Repository access**, choose **Only select repositories** and
      pick `aarthay/claude-website`.
   4. Under **Permissions → Repository permissions**, set **Contents** to
      **Read and write**. Leave everything else as it is.
   5. Click **Generate token** and copy it.

## Signing in

Click **Login** on the site (or go to `/admin/`), choose **Sign In Using Access
Token**, and paste your key. The browser remembers it, so you only do this once
per browser. Treat the key like a password: anyone who has it can change the
site. Use **Sign Out** on a shared computer.

## Adding artwork

1. In the admin area, open **Designs**, **Models** or **Sculptures** and click
   **New**.
2. Fill in the title and upload the image. Large photos are resized and
   converted to WebP in your browser before they are uploaded, so you can use
   photos straight from a camera or phone.
3. Optionally add a short image description (read aloud to blind visitors),
   the year, and a description.
4. **Position** sets the order: lower numbers come first. Numbering in tens
   (10, 20, 30) leaves room to slot new work in between.
5. Untick **Show on home page** to keep a piece off the home page grid. It
   still appears on its own section's page.
6. Click **Save**. The site updates in a minute or two.

Each artwork also gets its own page (for example `/artworks/flamingo/`), which
is what visitors reach when they share a link. On the site, clicking a tile
opens it full-screen, and the arrow keys or a swipe move between works.

## Editing pages, logos and contact details

- **Pages → About / Contact** edits the text on those pages. Anything in
  [square brackets] is placeholder text to replace.
- **Site settings** holds both logos (upload a new file to replace one), your
  email address, phone number and studio addresses. These appear on the
  Contact page.

## For developers

```sh
bundle install                   # Ruby 3.x
pip install Pillow               # Python 3
python3 scripts/make_images.py   # web-sized copies of the artwork, in assets/thumbs/
bundle exec jekyll serve         # http://localhost:4000
```

How it fits together:

| Path | What it is |
| --- | --- |
| `_artworks/` | One Markdown file per artwork. Front matter: `title`, `category` (`design`, `model` or `sculpture`), `image`, optional `alt`, `year`, `order`, `home`, and the description as the body. |
| `assets/artworks/` | Original uploads. |
| `assets/thumbs/` | Web copies made by `scripts/make_images.py` (480 and 960px wide tiles, 1800px viewer). Generated during each build and not committed. |
| `_data/settings.yml` | Logos and contact details. |
| `_includes/`, `_layouts/` | Header, gallery, viewer and page templates. |
| `assets/css/site.css`, `assets/js/gallery.js` | Styles and the full-screen viewer. |
| `admin/` | The admin area ([Sveltia CMS](https://github.com/sveltia/sveltia-cms)) and its `config.yml`. The CMS version is pinned in `admin/index.html`; bump it there and in the `$schema` line of `config.yml`. |
| `.github/workflows/pages.yml` | Builds and publishes the site on every push to `main`. |

All links go through Jekyll's `relative_url` filter, so the site works both at
`/claude-website/` and on a custom domain. If you add a custom domain, also
update `site_url`, `display_url` and `logout_redirect_url` in
`admin/config.yml`.

### Optional: a "Sign In with GitHub" button

The admin area uses access-token sign-in because it needs no server. For a
one-click **Sign In with GitHub** button instead, deploy
[sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) (a free
Cloudflare Worker), register a GitHub OAuth app for it, then in
`admin/config.yml` add `base_url: <your worker URL>` under `backend` and change
`auth_methods` to `[oauth, token]`.
