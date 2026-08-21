# Premium Landing Page Website Generator (Python)

Generates a complete, SEO-ready, premium-designed single landing page site
(HTML + Bootstrap 5.3 + custom CSS design system + Vanilla JS) — through a
**17-step browser wizard**, or from the command line.

Supports **5 site types**, driven by one flexible section engine:

| `site_type`   | Use case                          |
|---------------|------------------------------------|
| `supplement`  | Health / supplement product        |
| `education`   | Online course / academy            |
| `business`    | Agency / professional services     |
| `product`     | SaaS / general product             |
| `betting`     | Sportsbook / casino / gaming platform |

## Quick start — Web App (recommended)

```bash
pip install -r requirements.txt
python app.py --port 8000
```
Open **http://localhost:8000**. The wizard:

1. What kind of landing page? (supplement / education / business / product / betting)
2. Product / Course / Business name
3. Category
4. Official website / checkout URL (label adapts to the site type)
5. Primary SEO keyword
6. Secondary SEO keywords (comma-separated)
7. Your domain
8. Business / brand name
9. Contact email
10. Branding & pricing (colors + 3 tiers)
11. **Images** — favicon, og:image, twitter:image, hero/banner, main/"what is"
    image, ingredient images (supplement), customer photos, pricing tier
    images, certification badge, guarantee badge, discount badge. Anything
    left blank gets a styled placeholder at the exact right filename/size.
12. **Ingredient details** (supplement only) — enter your real ingredient
    names and their actual, factual role. Any row left blank keeps a
    generic placeholder in that slot instead.
13. **Customer testimonials** — enter real, verified quotes/names (up to 6,
    "Add another" reveals more). Always renders in a 3-column grid — blank
    rows are padded with placeholders so the layout never looks unbalanced.
14. **Choose your sections** — pick which of the 14 optional sections to
    include (Introduction, Why Choose Us, How It Works, Key Benefits,
    Ingredients, Guarantee, Stats, Testimonials, Pricing, What Happens Next,
    Urgency/Discount banner, FAQ, Conclusion). Banner (hero) and the final
    Call-to-Action are always included. Order is randomized automatically
    by default (toggle-able) — or use the up/down arrows on each card to
    set your own exact order, which turns randomization off for that
    generation.
15. **Reference sites** (optional) — paste competitor/inspiration URLs; a
    private `competitive-notes.md` is included in your download with each
    URL's title/meta description for your own research. **Competitor page
    content is never copied into your generated site.**
16. Pages & technical SEO — an automatic preview of every file that will be
    generated (no input needed).
17. Review & Generate — optionally check "Rewrite copy with AI" and paste
    your own Anthropic API key (used only for that one generation, sent
    directly to your local server, never written to disk or included in
    the downloaded zip) — then **Generate & Download ZIP**.

## Setting your Anthropic API key once (line by line)

Do this once, and you'll never need to paste a key into the wizard again
— Step 17 will show a green "server key found" note instead, automatically.

**1. Open a terminal in your `webgen` folder.** (In your case:
`cd C:\Users\ramkr\Desktop\Ram-All-Website\WebsiteLandingPageGenerator\webgen`
— adjust to wherever you unzipped it.)

**2. Install the two packages this needs** (if you haven't already):
```powershell
pip install anthropic python-dotenv
```

**3. Create your `.env` file from the template:**
```powershell
copy .env.example .env
```
This creates a new file called `.env` in the same folder as `app.py`.

**4. Open `.env` in Notepad** (or any text editor):
```powershell
notepad .env
```

**5. You'll see one line:**
```
ANTHROPIC_API_KEY=sk-ant-your-real-key-here
```
Replace `sk-ant-your-real-key-here` with your actual key from
console.anthropic.com — keep everything else on that line exactly as is
(no quotes, no spaces around the `=`).

**6. Save the file and close Notepad.**

**7. Run the app normally:**
```powershell
python app.py --port 8000
```

**8. Verify it worked** — open http://localhost:8000, go to Step 17, and
check "Rewrite copy with AI for fully unique wording." You should
immediately see a green box: *"A server-configured API key was found."*
That confirms it — you're done, forever, for every future generation on
this machine.

**Security notes:**
- `.gitignore` already excludes the real `.env` from git — only
  `.env.example` (which has no real key in it) is meant to ever be
  shared or committed.
- A real OS-level environment variable (set via `setx`/`export`) always
  takes priority over `.env` if you happen to have both set.
- If you ever want to use a *different* key for one specific generation,
  click "Use a different key for this generation instead" on that green
  note — it'll let you paste one just for that run without disturbing
  your saved `.env` key.

## Getting real content instead of placeholders

The template copy ("Key Ingredient 1 / Selected for its researched role...",
"Replace with a real, verified testimonial") exists because this tool has
no access to your actual product, formulation, or real customers — inventing
that would just be fabricated claims. To make a site fully real:

- **Ingredients (step 12)**: you supply the real ingredient names and a
  short, factual note on their role. Keep claims factual — avoid saying
  anything treats, cures, or prevents disease (that's an FDA/FTC issue,
  not just a content-quality one).
- **Testimonials (step 13)**: use real quotes from real customers who've
  given permission to be quoted (and ideally use their actual first
  name/last initial and a real photo you upload in step 11).
- **Everything else** (name, category, pricing, guarantee terms, contact
  info) is already driven directly by what you enter in steps 2-10 — there's
  no placeholder risk there once you fill in real values.
- **AI rewrite (step 17)** makes the *wording* more natural/unique, but it
  still starts from the ingredient/testimonial data you provided — it does
  not invent new ingredients or customers on its own.

## Hosting this on a server

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions to run
this on a real server instead of just your local machine — covers a
one-click PaaS option (Render), a Docker + VPS option with Nginx/HTTPS, and
a bare-metal gunicorn + systemd option. A `Dockerfile` and
`docker-compose.yml` are already included in this project.

## Betting / Gaming site type

The 5th vertical (`betting`) is built for sportsbooks, casinos, or other
gaming platforms — with its own hero, benefits, "how it works" (signup →
verify → deposit → bet), pricing reframed as welcome-bonus tiers, and FAQ
covering licensing, payouts, and account controls. It automatically
includes an `affiliate-disclosure.html` page and a dedicated
`responsible-gambling.html` page (deposit limits, self-exclusion tools, a
problem-gambling helpline reference), plus a footer age/responsible-play
notice — the same pattern used for the FDA notice on supplement sites.

## Manual section ordering + bug fix

The "Choose your sections" step had a real bug: navigating back to that
step silently rebuilt the entire list from defaults, wiping any selection
you'd made (this is what made Select All / Reset to recommended look
broken). Fixed — the list now only rebuilds when you actually change site
type.

On top of that fix, each section card now has up/down arrows so you can
set your own exact section order. A "Randomize order automatically"
toggle (on by default) controls whether your generation uses that manual
order or the zoned-random order described below — using the arrows
switches the toggle off automatically.

## Structural uniqueness — randomized section order & headings

Every time you generate a site, the section order and several headings come
out different — this matters if you're generating many sites with this
tool, since identical structure/wording across every output is a real
duplicate-content/template-fingerprint risk.

- **Section order** is "zoned" shuffled, not fully random: Banner is always
  first and the final CTA is always last; Introduction/What-Is-It stay near
  the top; Pricing/FAQ/Conclusion stay near the bottom; everything else
  (Why Choose, How It Works, Benefits, Ingredients, Guarantee, Stats,
  Testimonials, What Happens Next, Urgency) shuffles freely between them.
  This keeps the page reading as a coherent persuasive arc instead of
  putting FAQ before the product is even explained.
- **Headings vary too** — e.g. "What Is X?" / "Meet X" / "Getting to Know
  X" / "X, Explained" are chosen at random each generation, same for "Why
  Choose Us" and a few other section titles.
- **Grid item order** (Benefits, Why Choose, Stats cards) is shuffled too.
- The **section picker UI** (Step 14) intentionally stays in a stable order
  — randomizing where "Pricing" sits in that checklist every time you open
  the wizard would just make it harder to find what you're toggling. The
  randomization that matters for output uniqueness happens on the
  generated page itself, not the picker.

## Image handling: no cropping, no forced background color

Two real bugs are fixed here:

- **Placeholders no longer look like a harsh solid-color (or black) box.**
  Every "no photo yet" placeholder is now a soft, neutral gradient with a
  simple picture-frame icon and "Add your photo" label — looks intentional
  and premium even with a very dark brand color, instead of rendering as
  an ugly black/colored tile.
- **Hero and "What Is" images are no longer cropped, and never get an
  added background color.** Uploaded photos for these two slots are now
  resized to fit *without cropping* (the whole photo is preserved,
  whatever its original aspect ratio), rendered with `object-fit: contain`
  and a shadow that hugs the actual photo edges — not a rectangular
  colored box behind it. Other image slots (ingredient tiles, pricing
  cards, avatars) still use a tight cover-crop, since uniform framing
  matters more than showing 100% of the photo in a small grid tile.

## Legal pages: 10+ paragraphs each, and a real bug fix

All 8 legal pages (Privacy Policy, Disclaimer, Affiliate Disclosure,
Medical Disclaimer, Terms & Conditions, Shipping Policy, Refund Policy,
Responsible Gambling) now have at least 10 paragraphs of real content —
verified by generating actual sites and counting `<p>` tags, not
estimated. Along the way I found and fixed a real bug: the legal page
renderer was passing the Python function object itself into the template
instead of calling it, so pages were silently rendering almost no content
regardless of how much was written — this is why longer copy wasn't
showing up. **This is boilerplate, not legal advice** — have an actual
lawyer review these before you rely on them for a real business,
especially the medical/gambling-specific ones.

## Content depth: how it works, honestly

Template-mode (no AI) now generates roughly **1,650-1,700 words** per
supplement site with the default section selection — up from ~1,200
before this round, measured directly (not estimated) by generating real
sites and stripping HTML. Most of that jump came from 5 new sections
(below) with genuine content, not from padding existing ones further.

**If you need 2,000-3,000 words, enable AI rewrite (Step 17).** The prompt
explicitly instructs the model to hit that range in aggregate across all
body fields, with per-paragraph word-count rules and a self-check step —
but hand-written template copy has a practical ceiling before it turns
into repetitive filler, so template-only mode won't reliably reach
2,000-3,000 on its own. AI mode is the realistic path to a genuinely long,
non-repetitive page.

## 5 new sections

All selectable in Step 14 (auto-included by default where relevant to
your site type — no separate setup needed):

- **How to Use: Usage, Dosage & Directions** — supplement only. 5 paragraphs
  covering consistency, following label directions, storage, and a
  doctor-consultation note.
- **Pros & Cons** — all site types. An honest, balanced two-column
  comparison (green checkmarks / neutral gray) instead of only positive
  spin.
- **Free Bonuses** — all site types. 3 bonus-item cards; the copy is
  clearly generic ("customize these to match whatever bonuses you're
  actually offering") since this tool has no way to know your real bonus
  offer.
- **Free Shipping** — supplement only. Processing time, tracking,
  discreet packaging.
- **Where to Buy** — supplement and betting only (the two verticals where
  "only buy through the official site, avoid counterfeits/unofficial
  links" is genuinely relevant advice).

## Uploaded photos: zero processing, guaranteed

This went through a few iterations (an opt-in toggle, then auto-detection
based on how dark a photo's corners were) that kept causing edge-case
problems — including a visible artifact around fine details like dropper
caps, a side effect of the removal algorithm's flood-fill. The final,
simplest answer: **there is no background removal at all anymore.**

Every uploaded photo is used exactly as provided, whatever its
background — black, white, transparent, colored, anything. The *only*
operation ever applied to an uploaded image is resizing/cropping to fit
its section's layout box (unavoidable for consistent page layout, and
never touches color/content). If your source photo has a black backdrop,
the generated site will show that black backdrop, byte-for-byte
unchanged. Placeholder graphics (for slots you leave blank) are pure
white with a neutral gray icon — zero color contribution from the tool.

## Premium visual design

The generated site's design system includes: a gradient-text hero headline,
floating animated gradient blobs behind the hero, pulsing-dot eyebrow
labels, glassmorphic gradient-border-on-hover feature cards with icon
glow/tilt, a breathing glow + shimmer badge on the highlighted pricing
tier, a shine-sweep hover effect on primary buttons, and decorative
oversized quote marks on testimonial cards — all driven by your actual
chosen brand colors (including glow/tint effects, which are computed from
your real hex values, not a fixed color).

## Navbar & responsive design

The generated site's navbar is a curated menu — **Home, About, Benefits,
Ingredients (supplement only), Pricing, and a Buy Now button** — with a
logo monogram, underline-on-hover links, and a shadow that appears once the
page is scrolled. Every layout is mobile-first with explicit breakpoints
for phones, tablets, laptops, and desktops; images use `aspect-ratio` +
`object-fit: cover` so uploaded photos of any dimension never distort or
shift the layout, and the pricing "most popular" scale effect is disabled
below 992px to avoid edge clipping on narrow screens.

## Quick start — Command line

```bash
python -m pip install jinja2 pillow
python generate.py --interactive
# or
python generate.py --config config.example.json --output Products
```

Set `"selected_sections": ["what_is","pricing","faq"]` in a config to
customize sections from the CLI too (omit the key, or set it to `null`, to
get the recommended default set for that site type).

Set `"use_ai_content": true` (plus `ANTHROPIC_API_KEY`) to have every
section's copy rewritten uniquely by Claude instead of the built-in
templated wording.

## What gets generated

```
<slug>-website.zip
    index.html                  <- built from your selected sections
    privacy-policy.html
    disclaimer.html
    affiliate-disclosure.html   <- only for supplement / product types
    medical-disclaimer.html     <- only for supplement type
    terms-and-conditions.html
    shipping-policy.html
    refund-policy.html
    contact.html
    404.html
    sitemap.xml
    robots.txt
    .htaccess                   <- HTTPS redirect, custom 404, gzip, browser caching
    llms.txt                    <- plain-language site summary for AI crawlers
    competitive-notes.md        <- only if you provided reference-site URLs
    assets/
        css/style.css, responsive.css   <- premium design system, colorized to your brand
        js/script.js                    <- smooth scroll + scroll-reveal animation
        images/*.webp                   <- your uploaded images where provided, placeholders elsewhere
        images/manifest.json            <- filename, size, ALT, TITLE, AI image prompt for each
```

## Test the generated site locally

```bash
unzip <slug>-website.zip -d mysite
cd mysite/<Category>
python -m http.server 8000
```

## The section engine (12 optional + 2 mandatory)

Every landing page is an ordered Python list of **sections** — see
`site_content.py`. Sections you can toggle on/off in Step 12:

`intro`, `what_is`, `why_choose`, `how_it_works`, `benefits`, `ingredients`
(supplement only), `guarantee`, `stats`, `testimonials`, `pricing`,
`post_purchase`, `urgency`, `faq`, `conclusion`

`hero` (Banner) and `cta` (final Call-to-Action) are always included and
always first/last. Layouts backing these sections: `hero`, `split`, `text`,
`grid`, `steps`, `guarantee`, `urgency`, `stats`, `testimonials`, `pricing`,
`faq`, `cta` — all rendered by one template (`templates/index.html.j2`),
which is what lets both the section picker and all 4 verticals share one
engine. To add a new section type, write a `_my_section(cfg)` function in
`site_content.py`, add it to `BUILDERS`/`CANONICAL_ORDER`/`SECTION_META`,
and (if it needs a new visual shape) add a matching `{% elif s.layout == %}`
block to the template.

## On-page & technical SEO included

- Single `<h1>`, structured `<h2>`/`<h3>` hierarchy
- Meta title (≤60 chars), description (≤160 chars), keywords, canonical
- Open Graph + Twitter Card tags with dedicated og/twitter images
- JSON-LD schema: Organization, WebSite, FAQPage, BreadcrumbList, plus a
  type-aware primary schema (`Product` for supplement/product, `Course` for
  education, `Service` for business)
- Image ALT + TITLE on every image, SEO-friendly filenames
- `sitemap.xml`, `robots.txt`, `.htaccess`, `llms.txt`
- Internal links (footer, nav) to every legal page

## Project files

| File | Purpose |
|---|---|
| `app.py` | Flask web server — serves the wizard UI and `/api/generate`, `/api/sections`, `/api/site-types` |
| `webui/` | Browser wizard front-end (index.html, wizard.css, wizard.js) |
| `generate.py` | Core orchestrator — config validation + `build_site()`, used by both CLI and web app |
| `wizard.py` | CLI interactive prompts (terminal version of the wizard) |
| `site_content.py` | The section catalog engine + copy for all 4 site types |
| `ai_content.py` | Optional pass that rewrites section copy via the Anthropic API |
| `seo.py` | Meta tags, JSON-LD schema, sitemap.xml, robots.txt, `.htaccess`, `llms.txt` |
| `images.py` | Builds the image manifest, renders placeholders, applies uploaded images |
| `references.py` | Builds the optional `competitive-notes.md` from reference-site URLs |
| `color_suggest.py` | Derives a color palette from a reference site's favicon (Step 15) |
| `env_loader.py` | Loads a `.env` file (if present) so `ANTHROPIC_API_KEY` doesn't need OS-level env vars |
| `templates/*.j2` | Jinja2 HTML templates (index is layout-driven; legal/contact/404 shared) |
| `static/*` | Base CSS/JS for generated sites (colorized per-brand at generation time) |
| `config.*.example.json` | One example config per site type (for CLI use) |
| `Dockerfile` | Production container image (Gunicorn-based) |
| `docker-compose.yml` | One-command Docker deployment |
| `.dockerignore` | Keeps the Docker build context small |
| `DEPLOYMENT.md` | Step-by-step server hosting guide (Render, VPS+Docker, bare-metal) |

## Content depth & bullet points

- `_what_is` and other body-driven sections now write 2 paragraphs in
  template mode; when AI rewrite (Step 17) is enabled, body fields are
  explicitly expanded into 3-5 well-developed paragraphs instead of being
  rewritten at the same length as the template.
- Why Choose Us, Key Benefits, How It Works, and the Guarantee section now
  include a short bulleted highlights list above their cards.
- Fixed two real wording bugs: categories that already contain the word
  "Support" no longer produce "...Support Formula Support..." in the hero
  title, and setting your primary keyword to your own product name no
  longer produces "...trustworthy X are turning to X."

## Color palettes

Step 10 now includes 8 curated, professionally-balanced color palettes you
can apply with one click instead of hand-picking 4 hex values. Step 15
also has a "Suggest a primary color from this URL" button — it fetches
*only* the referenced site's favicon (never page content), extracts its
dominant color, and derives a full complementary palette from it. This is
best-effort and gracefully falls back to manual picking if the site has no
readable favicon.

## Animations

Grid/card rows now cascade in with a staggered reveal delay instead of all
fading in at once; the stats band counts up from 0 to its real value when
scrolled into view (skipped for non-numeric stats like "Lifetime"); the
hero image has a slow, continuous float. All animations respect
`prefers-reduced-motion` for users who've asked their OS to minimize
motion.

## Turning this into a hosted, multi-user SaaS

This is still a **local, single-user app** — run it on your own machine or a
private server. Going from here to a public, billable, multi-tenant SaaS
means adding genuinely separate pieces: accounts & auth, billing (Stripe),
persistent per-user storage, production deployment (Gunicorn/Nginx instead
of the Flask dev server), and abuse/rate-limiting on a public endpoint. The
generator engine itself (`generate.py`, `site_content.py`, `seo.py`,
`images.py`) doesn't change — a SaaS wrapper would call
`gen.build_site(cfg, output_root)` exactly like `app.py` does now. Say the
word if you want to build any one of those pieces next.

## Important note on content and compliance

The built-in supplement copy is intentionally generic and disease-claim-free.
If you enable AI content or write your own, keep an actual medical
disclaimer, avoid claiming a supplement treats/cures/prevents disease, and
follow FTC affiliate disclosure rules. This tool generates the disclaimer
pages and footer notice by default, but final legal/regulatory review of
your copy is on you.
