"""
site_content.py
----------------
Section-catalog content engine.

Every landing page is an ordered list of "sections". Each section is a
plain dict with a `layout` key telling the template how to render it.
`hero` and `cta` are mandatory and always included; every other
section is optional and user-selectable (Step 13 of the wizard).

Layouts implemented:
    hero          - big banner, title, subtitle, CTA, image, trust badges
    split         - image + text, alternating sides
    text          - centered text block
    grid          - icon feature cards (3-4 columns)
    steps         - numbered process cards (how it works / after checkout)
    guarantee     - centered badge + reassurance copy
    urgency       - bold banner pushing a limited-time action
    stats         - big-number stat band
    pricing       - 3-tier pricing cards
    testimonials  - quote cards with avatar
    team          - people cards
    faq           - accordion
    cta           - full-width gradient call-to-action band

Each section may include:
    id            - used for the #anchor, nav, and section picker
    layout        - one of the layouts above
    theme         - "light" | "alt" | "brand" (assigned automatically,
                    can be overridden by FORCED_THEME below)
    eyebrow       - small label above the title
    title, body   - main copy (body is HTML)
    image         - {"suffix","alt","w","h"} -> assets/images/<slug>-<suffix>.webp
    reverse       - bool, for split layout (flip image/text sides)
    items         - layout-specific list
    cta           - {"label","href"}
    show_in_nav   - bool, include in the top navbar
"""

import random

SITE_TYPES = ["supplement", "education", "business", "product", "betting"]


def _avoid_dupe_suffix(category, suffix_word):
    """Returns '' if the category the user typed already contains the
    word we'd otherwise append (e.g. category='Heart Health Support
    Formula' + suffix_word='Support' -> ''), else returns ' ' + suffix_word.
    Prevents awkward duplication like 'Support Formula Support'."""
    return "" if suffix_word.lower() in category.lower() else f" {suffix_word}"


def _safe_keyword(cfg):
    """Some users set the primary keyword to their brand/product name
    itself, which breaks sentences like 'searching for a trustworthy
    {keyword} are turning to {product_name}' (X ... X). Falls back to a
    category-based phrase in that case."""
    pk = cfg["primary_keyword"]
    if pk.strip().lower() == cfg["product_name"].strip().lower():
        return f"{cfg['category'].lower()} solution"
    return pk


def _support_verb_phrase(category):
    """'formulated to support {category}' reads badly when the category
    itself already contains the word 'support' (e.g. 'Heart Health
    Support Formula' -> 'formulated to support heart health support
    formula'). Swap in a verb that doesn't repeat it."""
    return "designed around" if "support" in category.lower() else "formulated to support"


def _img(suffix, alt, w=1200, h=900):
    return {"suffix": suffix, "alt": alt, "w": w, "h": h}


# =======================================================================
# SECTION CATALOG METADATA (drives the wizard's "choose your sections" UI)
# =======================================================================
CANONICAL_ORDER = [
    "intro", "what_is", "why_choose", "how_it_works", "usage", "benefits",
    "pros_cons", "ingredients", "guarantee", "bonuses", "shipping", "stats",
    "testimonials", "pricing", "post_purchase", "urgency", "where_to_buy",
    "faq", "conclusion",
]

SECTION_META = {
    "intro":         ("Introduction", "Short framing of why this exists"),
    "what_is":       ("What Is It?", "Explains the product / course / service"),
    "why_choose":    ("Why Choose Us", "Reasons to pick you over alternatives"),
    "how_it_works":  ("How Does It Work?", "Step-by-step process"),
    "usage":         ("How to Use", "Usage, dosage & directions (supplement only)"),
    "benefits":      ("Key Benefits", "Icon grid of top benefits"),
    "pros_cons":     ("Pros & Cons", "Honest, balanced pros and cons"),
    "ingredients":   ("Natural Ingredients", "Ingredient breakdown (supplement only)"),
    "guarantee":     ("Money-Back Guarantee", "Guarantee / satisfaction promise"),
    "bonuses":       ("Free Bonuses", "Bonus items included with purchase"),
    "shipping":      ("Free Shipping", "Shipping & delivery details (supplement only)"),
    "stats":         ("Stats Band", "Social proof numbers"),
    "testimonials":  ("Customer Testimonials", "What customers are saying"),
    "pricing":       ("Pricing", "Pricing tiers"),
    "post_purchase": ("What Happens Next", "What happens after checkout / signup"),
    "urgency":       ("Limited-Time Urgency", "\"Don't wait\" discount banner"),
    "where_to_buy":  ("Where to Buy", "Where to purchase safely (supplement/betting)"),
    "faq":           ("FAQ", "Frequently asked questions"),
    "conclusion":    ("Conclusion", "Closing summary before the final CTA"),
}

def _exclude(*ids):
    return [s for s in CANONICAL_ORDER if s not in ids]

AVAILABLE_BY_TYPE = {
    "supplement": list(CANONICAL_ORDER),
    "education": _exclude("ingredients", "usage", "shipping", "where_to_buy"),
    "business": _exclude("ingredients", "usage", "shipping", "where_to_buy"),
    "product": _exclude("ingredients", "usage", "shipping", "where_to_buy"),
    "betting": _exclude("ingredients", "usage", "shipping"),
}

DEFAULT_SELECTED = {
    "supplement": ["intro", "what_is", "why_choose", "how_it_works", "usage", "benefits",
                   "pros_cons", "ingredients", "guarantee", "bonuses", "shipping", "stats",
                   "testimonials", "pricing", "post_purchase", "urgency", "where_to_buy",
                   "faq", "conclusion"],
    "education": ["intro", "what_is", "why_choose", "how_it_works", "benefits", "pros_cons",
                  "guarantee", "bonuses", "stats", "testimonials", "pricing", "faq", "conclusion"],
    "business": ["intro", "what_is", "why_choose", "how_it_works", "benefits", "pros_cons",
                 "bonuses", "stats", "testimonials", "pricing", "faq", "conclusion"],
    "product": ["intro", "what_is", "why_choose", "how_it_works", "benefits", "pros_cons",
                "guarantee", "bonuses", "stats", "testimonials", "pricing", "faq", "conclusion"],
    "betting": ["intro", "what_is", "why_choose", "how_it_works", "benefits", "pros_cons",
                "guarantee", "bonuses", "stats", "testimonials", "pricing",
                "post_purchase", "urgency", "where_to_buy", "faq", "conclusion"],
}

FORCED_THEME = {"stats": "brand", "urgency": "brand"}

# Curated top-nav menu: Home (always, points to hero) + these sections
# (in this fixed order) when they're selected, each with a short,
# consistent nav label distinct from the (longer, type-specific) section
# heading -- then Buy Now / the primary CTA always last.
NAV_LABELS = {
    "what_is": "About",
    "benefits": "Benefits",
    "ingredients": "Ingredients",
    "pricing": "Pricing",
}
NAV_CANDIDATES = set(NAV_LABELS.keys())


def get_section_catalog(site_type):
    """Returns the picker data for the wizard: ordered list of
    {id, label, description, default_checked} for this site type."""
    available = AVAILABLE_BY_TYPE.get(site_type, AVAILABLE_BY_TYPE["product"])
    defaults = set(DEFAULT_SELECTED.get(site_type, available))
    return [
        {"id": sid, "label": SECTION_META[sid][0], "description": SECTION_META[sid][1],
         "default_checked": sid in defaults}
        for sid in CANONICAL_ORDER if sid in available
    ]


# =======================================================================
# HERO (mandatory, first)
# =======================================================================
HERO_COPY = {
    "supplement": lambda cfg: {
        "eyebrow": cfg["category"],
        "title": f"{cfg['product_name']} — Premium {cfg['category']}{_avoid_dupe_suffix(cfg['category'], 'Support')}, Backed by Science",
        "body": (f"<p>Discover why thousands of people searching for a trustworthy "
                  f"{_safe_keyword(cfg)} are turning to {cfg['product_name']}. "
                  f"Formulated with researched ingredients and made for real, "
                  f"everyday results.</p>"
                  f"<p>No proprietary-blend guesswork, no filler — just a formula "
                  f"built to a consistent standard, batch after batch.</p>"),
        "cta_label": f"Get {cfg['product_name']} Now",
        "trust_badges": ["GMP Certified", "Non-GMO", "Lab Tested", "30-Day Guarantee"],
    },
    "education": lambda cfg: {
        "eyebrow": cfg["category"],
        "title": f"{cfg['product_name']} — Learn {cfg['category']} the Right Way",
        "body": (f"<p>A practical, project-based course for anyone searching for "
                  f"{_safe_keyword(cfg)}. No fluff, no filler — just a clear "
                  f"path from beginner to confident practitioner.</p>"
                  f"<p>Every lesson is built to be applied immediately, not just "
                  f"watched — so what you learn actually sticks.</p>"),
        "cta_label": "Enroll Now",
        "trust_badges": ["Lifetime Access", "Certificate Included", "Beginner Friendly", "Self-Paced"],
    },
    "business": lambda cfg: {
        "eyebrow": cfg["category"],
        "title": f"{cfg['product_name']} — {cfg['category']} That Actually Moves the Needle",
        "body": (f"<p>We help businesses searching for {_safe_keyword(cfg)} get "
                  f"measurable results, without the agency jargon or bloated "
                  f"retainers.</p>"
                  f"<p>A clear plan, a real team behind it, and reporting you can "
                  f"actually understand — that's the whole approach.</p>"),
        "cta_label": "Get a Free Consultation",
        "trust_badges": ["Trusted by 100+ Clients", "5+ Years Experience", "Transparent Pricing", "No Long-Term Lock-In"],
    },
    "product": lambda cfg: {
        "eyebrow": cfg["category"],
        "title": f"{cfg['product_name']} — {cfg['category']} Made Simple",
        "body": (f"<p>{cfg['product_name']} is built for people searching for "
                  f"{_safe_keyword(cfg)} who want something that just works, "
                  f"from day one.</p>"
                  f"<p>No steep learning curve, no bloated feature list you'll "
                  f"never touch — just the essentials, done well.</p>"),
        "cta_label": "Start Free Trial",
        "trust_badges": ["No Credit Card Required", "Cancel Anytime", "Free 14-Day Trial", "5-Star Support"],
    },
    "betting": lambda cfg: {
        "eyebrow": cfg["category"],
        "title": f"{cfg['product_name']} — {cfg['category']} You Can Trust",
        "body": (f"<p>Discover why players searching for a reliable "
                  f"{_safe_keyword(cfg)} are choosing {cfg['product_name']}. "
                  f"Licensed, secure, and built for a fair, fast experience.</p>"
                  f"<p>Competitive odds, quick verification, and payouts that "
                  f"actually show up on time — no fine-print surprises.</p>"),
        "cta_label": "Claim Your Bonus",
        "trust_badges": ["Licensed & Regulated", "Fast Payouts", "Secure Deposits", "24/7 Support"],
    },
}


def _hero(cfg):
    copy = HERO_COPY.get(cfg["site_type"], HERO_COPY["product"])(cfg)
    return {
        "id": "hero", "layout": "hero", "theme": "light",
        "eyebrow": copy["eyebrow"], "title": copy["title"], "body": copy["body"],
        "image": _img("hero", f"{cfg['product_name']} {cfg['category']} hero banner", 1600, 900),
        "badge_image": _img("certified", "Certification / trust badge", 300, 300),
        "cta": {"label": copy["cta_label"], "href": cfg["affiliate_link"]},
        "trust_badges": copy["trust_badges"],
    }


# =======================================================================
# INTRO
# =======================================================================
def _intro(cfg):
    name, cat = cfg["product_name"], cfg["category"]
    body = {
        "supplement": (
            f"<p>{name} is a premium {cat.lower()} formula designed for people "
            f"who are done guessing and ready for a straightforward, "
            f"ingredient-transparent approach.</p>"
            f"<p>No proprietary blends hiding the actual doses, no vague marketing "
            f"claims — just a formula you can actually understand before you "
            f"decide to try it.</p>"
        ),
        "education": (
            f"<p>{name} exists for one reason: most {cat.lower()} content out "
            f"there is either too shallow to be useful or too advanced to start "
            f"with. This course sits in between — practical from lesson one.</p>"
            f"<p>You won't find filler modules padding out a course length here "
            f"— every lesson exists because it teaches something you'll actually "
            f"use.</p>"
        ),
        "business": (
            f"<p>{name} was built for businesses who've tried {cat.lower()} "
            f"before and got vague promises instead of results. We do things "
            f"differently.</p>"
            f"<p>That means real numbers, real accountability, and a team that "
            f"treats your business like it's worth taking seriously — because "
            f"it is.</p>"
        ),
        "product": (
            f"<p>{name} was built to remove the busywork from {cat.lower()}, so "
            f"you can spend less time managing tools and more time doing the "
            f"work that matters.</p>"
            f"<p>It's the kind of product that gets out of your way once it's "
            f"set up — not one more thing demanding your attention every day.</p>"
        ),
        "betting": (
            f"<p>{name} exists for players who are tired of shady platforms and "
            f"slow payouts. {cat} should be exciting, not stressful.</p>"
            f"<p>That means transparent odds, fast verification, and a platform "
            f"that treats your account — and your winnings — with the respect "
            f"they deserve.</p>"
        ),
    }
    return {
        "id": "intro", "layout": "text", "title": None, "show_in_nav": False,
        "body": body.get(cfg["site_type"], body["product"]),
    }


# =======================================================================
# WHAT IS IT (split)
# =======================================================================
def _what_is(cfg):
    name, cat, sk = cfg["product_name"], cfg["category"], cfg.get("secondary_keywords", [])
    pk = _safe_keyword(cfg)
    body = {
        "supplement": (
            f"<p>{name} is a dietary supplement {_support_verb_phrase(cat)} {cat.lower()}. "
            f"It combines a targeted blend of ingredients selected for their role in "
            f"{sk[0] if sk else pk}, made to a consistent standard in every batch.</p>"
            f"<p>Rather than relying on a single ingredient, {name} takes a layered "
            f"approach — every serving is measured precisely, so what's printed on "
            f"the label is exactly what ends up in the bottle you receive.</p>"
            f"<p>It's built for people who want a straightforward daily habit, not a "
            f"complicated regimen — one serving, at roughly the same time each day, "
            f"is all it takes to stay consistent.</p>"
        ),
        "education": (
            f"<p>{name} walks you step-by-step through {cat.lower()}, combining short "
            f"video lessons with hands-on exercises so you actually retain what you "
            f"learn instead of just watching someone else do it.</p>"
            f"<p>Each module builds directly on the last, so by the end you're not "
            f"just familiar with the concepts — you've applied them to real projects "
            f"you can point to and talk through.</p>"
            f"<p>You move at your own pace, revisiting any lesson as often as you "
            f"need, with no pressure to keep up with a fixed class schedule.</p>"
        ),
        "business": (
            f"<p>{name} is a {cat.lower()} partner for businesses that want a "
            f"straightforward plan, clear reporting, and a team that treats their "
            f"budget like it matters — because it does.</p>"
            f"<p>No jargon-filled decks, no vague monthly summaries — just a plan you "
            f"understand, work you can see happening, and results you can actually "
            f"measure against what you started with.</p>"
            f"<p>You get a dedicated point of contact instead of a rotating cast of "
            f"account managers, so context never gets lost between conversations.</p>"
        ),
        "product": (
            f"<p>{name} is a {cat.lower()} product designed to remove the busywork so "
            f"you can focus on what actually matters, without adding another tool "
            f"you have to babysit.</p>"
            f"<p>It's built to fit into how your team already works, not force you to "
            f"change everything just to adopt one more piece of software.</p>"
            f"<p>Setup takes minutes, not a multi-week rollout, and the interface "
            f"stays out of your way once you're up and running.</p>"
        ),
        "betting": (
            f"<p>{name} is a {cat.lower()} platform built around fair odds, fast "
            f"verification, and payouts that actually arrive on time instead of "
            f"getting stuck in review.</p>"
            f"<p>Every account is protected with industry-standard security, and every "
            f"market is priced to stay competitive — not a bait-and-switch on odds "
            f"once you've already signed up and deposited.</p>"
            f"<p>Whether you're new to betting or have done this for years, the "
            f"platform is built to be usable without a learning curve getting in "
            f"the way.</p>"
        ),
    }
    alt = f"{name} bottle product photo" if cfg["site_type"] == "supplement" else f"{name} preview"
    title_variants = [
        f"What Is {name}?",
        f"Meet {name}",
        f"Getting to Know {name}",
        f"{name}, Explained",
    ]
    return {
        "id": "what_is", "layout": "split", "reverse": False,
        "eyebrow": "About", "title": random.choice(title_variants),
        "body": body.get(cfg["site_type"], body["product"]),
        "image": _img("product-main", alt, 1200, 1200),
    }


# =======================================================================
# WHY CHOOSE US (grid)
# =======================================================================
def _why_choose(cfg):
    name = cfg["product_name"]
    items = {
        "supplement": [
            {"icon": "bi-check2-circle", "title": "Clean Label", "text": "No hidden proprietary blends — every ingredient and amount is listed."},
            {"icon": "bi-flask", "title": "Third-Party Tested", "text": "Every batch is tested for purity and potency."},
            {"icon": "bi-truck", "title": "Fast Shipping", "text": "Orders ship quickly, with tracking included."},
            {"icon": "bi-headset", "title": "Real Support", "text": "A real team behind the product, not a chatbot loop."},
        ],
        "education": [
            {"icon": "bi-person-workspace", "title": "Built by a Practitioner", "text": "Taught by someone who actually does this work."},
            {"icon": "bi-kanban", "title": "Project-Based", "text": "You build real things, not just watch slides."},
            {"icon": "bi-infinity", "title": "Lifetime Access", "text": "Revisit any lesson, anytime, at no extra cost."},
            {"icon": "bi-people", "title": "Community Support", "text": "You're not learning alone."},
        ],
        "business": [
            {"icon": "bi-eye", "title": "Full Transparency", "text": "You always know exactly what we're doing and why."},
            {"icon": "bi-graph-up-arrow", "title": "Results-Focused", "text": "We report on outcomes, not vanity metrics."},
            {"icon": "bi-clock-history", "title": "No Long Lock-In", "text": "Flexible terms — we earn your business every month."},
            {"icon": "bi-people", "title": "A Real Team", "text": "Direct access to the people doing the work."},
        ],
        "product": [
            {"icon": "bi-lightning-charge", "title": "Fast to Adopt", "text": "Your team can be productive on day one."},
            {"icon": "bi-shield-check", "title": "Secure by Default", "text": "Enterprise-grade security, no extra setup."},
            {"icon": "bi-arrows-angle-expand", "title": "Scales With You", "text": "From solo use to enterprise teams."},
            {"icon": "bi-headset", "title": "Real Support", "text": "Talk to a real human when you need help."},
        ],
        "betting": [
            {"icon": "bi-shield-check", "title": "Licensed & Regulated", "text": "Operating under proper licensing, not an offshore gray-market site."},
            {"icon": "bi-lightning-charge", "title": "Fast Payouts", "text": "Withdrawals processed quickly, not held up for days."},
            {"icon": "bi-graph-up-arrow", "title": "Competitive Odds", "text": "Pricing that stays fair after you've signed up, not just in the ads."},
            {"icon": "bi-headset", "title": "Real Support", "text": "24/7 support from people, not just a bot loop."},
        ],
    }
    chosen_items = items.get(cfg["site_type"], items["product"])[:]
    random.shuffle(chosen_items)
    title_variants = [
        f"Why Choose {name}",
        f"What Makes {name} Different",
        f"The {name} Difference",
        f"Why {name} Stands Out",
    ]
    intro_body = {
        "supplement": f"<p>There's no shortage of options in {cfg['category'].lower()} — here's what actually sets {name} apart.</p>",
        "education": f"<p>Plenty of courses cover {cfg['category'].lower()} — here's what makes learning it with {name} different.</p>",
        "business": f"<p>You have options for {cfg['category'].lower()} — here's why teams choose {name} specifically.</p>",
        "product": f"<p>There's no shortage of tools for {cfg['category'].lower()} — here's what makes {name} the one worth switching to.</p>",
        "betting": f"<p>There's no shortage of betting platforms out there — here's what actually sets {name} apart from the rest.</p>",
    }
    return {
        "id": "why_choose", "layout": "grid",
        "eyebrow": "Why Choose Us", "title": random.choice(title_variants),
        "body": intro_body.get(cfg["site_type"], intro_body["product"]),
        "bullets": [item["title"] for item in chosen_items],
        "items": chosen_items,
    }


# =======================================================================
# HOW IT WORKS (steps)
# =======================================================================
def _how_it_works(cfg):
    name = cfg["product_name"]
    body = {
        "supplement": (
            f"<p>Getting results from {name} doesn't require a complicated protocol "
            f"— just a simple routine, done consistently. Everything starts with "
            f"your daily serving, taken as directed on the label, ideally at the "
            f"same time each day.</p>"
            f"<p>Most people find it easiest to build it into something they "
            f"already do — with breakfast, alongside a morning coffee, or right "
            f"after brushing their teeth. The goal isn't perfection, just "
            f"consistency you can actually keep up.</p>"
            f"<p>From there, it's mostly about staying the course. The formula "
            f"needs time to work with your body, so most people notice changes "
            f"building gradually over 30 to 90 days rather than overnight.</p>"
            f"<p>Along the way, it helps to pay attention to how you're actually "
            f"feeling — small shifts add up, even when they're not dramatic "
            f"enough to notice day to day.</p>"
            f"<p>Once you've found your rhythm, a multi-bottle package locks in "
            f"your lowest price per bottle and means you're never caught without "
            f"a refill mid-routine.</p>"
            f"<p>Some people also find it helps to keep a simple note of when "
            f"they started — a quick mental marker makes it easier to notice "
            f"real change instead of guessing at timelines later.</p>"
            f"<p>If you ever have questions along the way, our support team is "
            f"available to help — you're never left to figure things out on "
            f"your own.</p>"
        ),
        "education": (
            f"<p>{name} is structured so you always know exactly what to do next "
            f"— no guessing which lesson to start with or wondering if you're "
            f"missing something important.</p>"
            f"<p>Once you enroll, you get instant access to every current module, "
            f"so you can start right away instead of waiting on a fixed class "
            f"schedule to catch up to you.</p>"
            f"<p>From there, you work through the material at your own pace — in "
            f"order if you want a guided path, or by topic if you already know "
            f"what you're looking to fix.</p>"
            f"<p>Each module pushes you to apply what you've learned to a real "
            f"project, not just watch and forget, so the skills actually stick "
            f"once the course is finished.</p>"
            f"<p>Finish all the modules and you'll earn a certificate — proof of "
            f"the work, not just a participation badge for showing up.</p>"
            f"<p>If you ever get stuck, community support and Q&amp;A sessions are "
            f"there to help — you're not expected to figure everything out "
            f"completely on your own.</p>"
            f"<p>And once you finish, lifetime access means you can always come "
            f"back to refresh a concept or revisit a module you want to "
            f"revisit.</p>"
        ),
        "business": (
            f"<p>Working with {name} follows a clear process from first "
            f"conversation to ongoing results — no black box, no vague promises "
            f"about what happens behind the scenes.</p>"
            f"<p>It starts with a free consultation, where we learn about your "
            f"goals, your current numbers, and what budget you're actually "
            f"working with — no generic sales pitch.</p>"
            f"<p>From there, you get a custom plan built around what you told us, "
            f"prioritized by what will move the needle first, not a templated "
            f"package we hand to every client.</p>"
            f"<p>Once you approve it, our team gets to work, with regular "
            f"check-ins so you're never left wondering what's happening with "
            f"your account.</p>"
            f"<p>Throughout, you get transparent reporting in plain English, so "
            f"you always know what's working and what we're adjusting next.</p>"
            f"<p>As results come in, we revisit the plan together — doubling down "
            f"on what's working and cutting what isn't, rather than sticking to "
            f"a plan just because it was the original one.</p>"
            f"<p>Along the way, you always have a real point of contact — not a "
            f"rotating cast of account managers who don't know your history.</p>"
        ),
        "product": (
            f"<p>Getting set up with {name} takes minutes, not weeks — here's "
            f"exactly what that looks like from the moment you sign up.</p>"
            f"<p>You start with a free account, no credit card required, so you "
            f"can actually try things out before committing to anything.</p>"
            f"<p>From there, quick setup lets you import your existing data or "
            f"start fresh — whichever fits how your team already works.</p>"
            f"<p>Once you're in, invite your team with a click, and everyone can "
            f"start collaborating in the same workspace right away.</p>"
            f"<p>As your needs grow, you can scale up whenever you actually need "
            f"more — never paying for capacity you're not using yet.</p>"
            f"<p>Along the way, in-app guidance and a responsive support team mean "
            f"you're never stuck figuring things out entirely by trial and "
            f"error.</p>"
            f"<p>And since everything is cloud-based, your whole team stays in "
            f"sync automatically — no manual exports or version-mismatch "
            f"headaches.</p>"
        ),
        "betting": (
            f"<p>Getting started with {name} takes just a few minutes — here's "
            f"exactly what happens from signup to placing your first bet.</p>"
            f"<p>First, you create an account and verify your age and identity "
            f"— a quick step that keeps the platform compliant and your account "
            f"secure.</p>"
            f"<p>Next, you fund your account through a secure payment method, "
            f"choosing from whichever deposit option works best for you.</p>"
            f"<p>From there, you can explore the markets — browsing live odds and "
            f"lines across whatever sports or events you're interested in "
            f"betting on.</p>"
            f"<p>When you've found a bet you like, confirm your wager and track "
            f"it in real time, right up until the event settles.</p>"
            f"<p>If your bet wins, payouts are processed promptly to your chosen "
            f"withdrawal method — no chasing down support to release your "
            f"funds.</p>"
            f"<p>And if you ever want a break, deposit limits and self-exclusion "
            f"tools are built right into your account settings, ready whenever "
            f"you need them.</p>"
        ),
    }
    bullets = {
        "supplement": ["No complicated protocol", "Fits into your existing routine", "Results build over weeks, not days"],
        "education": ["Learn at your own pace", "Real projects, not just theory", "Certificate on completion"],
        "business": ["Clear plan before any work starts", "Regular check-ins, no surprises", "Transparent reporting throughout"],
        "product": ["Live in minutes, not weeks", "No steep learning curve", "Works with your existing tools"],
        "betting": ["Account verification in minutes", "Multiple secure deposit options", "Bets tracked in real time"],
    }
    return {
        "id": "how_it_works", "layout": "text", "align_left": True,
        "full_width": True, "columns": True,
        "eyebrow": "The Process", "title": f"How Does {name} Work?",
        "body": body.get(cfg["site_type"], body["product"]),
        "bullets": bullets.get(cfg["site_type"], bullets["product"]),
    }


# =======================================================================
# BENEFITS (grid)
# =======================================================================
def _benefits(cfg):
    cat, sk = cfg["category"], cfg.get("secondary_keywords", [])
    if cfg["site_type"] == "supplement":
        items = [
            {"icon": "bi-shield-check", "title": (sk[0] if len(sk) > 0 else "Targeted Support").capitalize(),
             "text": f"Formulated to support {cat.lower()} as part of your daily routine."},
            {"icon": "bi-capsule", "title": (sk[1] if len(sk) > 1 else "Clean Formula").capitalize(),
             "text": "Clearly labeled ingredients, nothing hidden behind a proprietary blend."},
            {"icon": "bi-calendar-check", "title": "Simple Routine",
             "text": "One easy serving a day, no complicated protocols."},
            {"icon": "bi-award", "title": "Guaranteed",
             "text": "Backed by our satisfaction guarantee, risk-free to try."},
        ]
        title = "Key Benefits"
    elif cfg["site_type"] == "education":
        items = [
            {"icon": "bi-play-circle", "title": "Module 1: Foundations", "text": "Core concepts you need before anything else clicks."},
            {"icon": "bi-diagram-3", "title": "Module 2: Core Skills", "text": "The hands-on techniques that make up the bulk of real work."},
            {"icon": "bi-kanban", "title": "Module 3: Real Projects", "text": "Apply everything to projects you can add to your portfolio."},
            {"icon": "bi-trophy", "title": "Module 4: Next Steps", "text": "How to keep growing after this course."},
        ]
        title = "What's Inside"
    elif cfg["site_type"] == "business":
        items = [
            {"icon": "bi-graph-up-arrow", "title": "Strategy", "text": "A clear, prioritized plan built around your goals and budget."},
            {"icon": "bi-people", "title": "Execution", "text": "A dedicated team that actually does the work, not just advises on it."},
            {"icon": "bi-bar-chart", "title": "Reporting", "text": "Plain-English reporting so you always know what's working."},
            {"icon": "bi-headset", "title": "Support", "text": "Direct access to your team — no ticket queues."},
        ]
        title = "How We Help"
    elif cfg["site_type"] == "betting":
        items = [
            {"icon": "bi-graph-up", "title": "Live Odds", "text": "Real-time pricing across a wide range of markets."},
            {"icon": "bi-phone", "title": "Mobile Friendly", "text": "Bet from anywhere, fully optimized for mobile."},
            {"icon": "bi-lightning-charge", "title": "Fast Payouts", "text": "Withdrawals processed quickly, not held for days."},
            {"icon": "bi-shield-lock", "title": "Secure Platform", "text": "Your funds and data protected with industry-standard security."},
        ]
        title = "Key Features"
    else:
        items = [
            {"icon": "bi-lightning-charge", "title": "Fast Setup", "text": "Get up and running in minutes, not days."},
            {"icon": "bi-shield-lock", "title": "Secure by Default", "text": "Your data is encrypted and protected end-to-end."},
            {"icon": "bi-plug", "title": "Integrates Easily", "text": "Connects with the tools you already use."},
            {"icon": "bi-graph-up", "title": "Built to Scale", "text": "Works whether you're a team of 1 or 1,000."},
        ]
        title = "Everything You Need"

    title_variants = {
        "supplement": ["Key Benefits", "Why It Works For You", "What You Get"],
        "education": ["What's Inside", "Course Curriculum", "What You'll Learn"],
        "business": ["How We Help", "What We Bring to the Table", "Our Approach"],
        "product": ["Everything You Need", "Built-In Features", "What's Included"],
        "betting": ["Key Features", "What You Get", "Platform Highlights"],
    }
    items = items[:]
    random.shuffle(items)
    title = random.choice(title_variants.get(cfg["site_type"], title_variants["product"]))

    intro_body = {
        "supplement": f"<p>Every part of {cfg['product_name']} is built around one goal: real, everyday {cfg['category'].lower()} — not just a label full of promises.</p>",
        "education": f"<p>{cfg['product_name']} is organized so each module builds directly on the last, with a clear point at the end.</p>",
        "business": f"<p>{cfg['product_name']} covers the full picture — not just one piece of {cfg['category'].lower()} while leaving the rest to you.</p>",
        "product": f"<p>{cfg['product_name']} bundles the essentials so you're not stitching together five different tools.</p>",
        "betting": f"<p>{cfg['product_name']} is built around the things that actually matter to bettors — fair pricing, real-time markets, and a platform that stays up when it counts.</p>",
    }

    return {
        "id": "benefits", "layout": "grid",
        "eyebrow": "Why It Works", "title": title,
        "body": intro_body.get(cfg["site_type"], intro_body["product"]),
        "bullets": [item["title"] for item in items],
        "items": items,
    }


# =======================================================================
# INGREDIENTS (supplement only)
# =======================================================================
def _ingredients(cfg):
    if cfg["site_type"] != "supplement":
        return None
    name = cfg["product_name"]
    real = cfg.get("ingredients_data") or []
    real = real[:10]  # hard cap at 10
    icons = ["bi-flower1", "bi-flower2", "bi-flower3", "bi-tree",
             "bi-droplet", "bi-sun", "bi-snow", "bi-leaf", "bi-gem", "bi-stars"]

    if real:
        # Pad up to 4 minimum for a balanced grid row; beyond 4, use
        # exactly what was provided (no forced padding to a round number).
        slot_count = max(4, len(real))
        items = []
        for i in range(slot_count):
            if i < len(real):
                ing_name = real[i].get("name", "").strip() or f"Key Ingredient {i + 1}"
                ing_desc = real[i].get("description", "").strip() or "Selected for its researched role in this category."
            else:
                ing_name = f"Key Ingredient {i + 1}"
                ing_desc = "Selected for its researched role in this category."
            items.append({
                "icon": icons[i % len(icons)], "title": ing_name, "text": ing_desc,
                "image": _img(f"ingredient-{i + 1}", ing_name, 600, 600),
            })
    else:
        items = [
            {"icon": icons[i], "title": f"Key Ingredient {i + 1}",
             "text": "Selected for its researched role in this category.",
             "image": _img(f"ingredient-{i + 1}", f"Key ingredient {i + 1}", 600, 600)}
            for i in range(4)
        ]

    return {
        "id": "ingredients", "layout": "grid",
        "eyebrow": "Inside Every Capsule", "title": f"The Natural Ingredients in {name}",
        "items": items,
    }


# =======================================================================
# GUARANTEE
# =======================================================================
GUARANTEE_COPY = {
    "supplement": lambda name: (f"Our {name} Guarantee",
        f"<p>{name} is backed by a 30-day money-back guarantee. If it's not "
        f"the right fit for you, reach out to our support team for a refund "
        f"per the terms on our Refund Policy page — no complicated hoops to "
        f"jump through.</p>"
        f"<p>We'd rather you try it risk-free than take our word for it — "
        f"that's the whole point of backing it with a real guarantee instead "
        f"of just a marketing claim.</p>"),
    "education": lambda name: ("Our Guarantee",
        f"<p>If {name} isn't the right fit within the first 14 days, "
        f"contact us for a refund per our Refund Policy page. We'd rather "
        f"you get real value than feel stuck.</p>"
        f"<p>There's no awkward exit interview or hoop-jumping required — "
        f"just a straightforward request through support.</p>"),
    "business": lambda name: ("Our Promise",
        f"<p>{name} works on flexible terms with clear reporting — if we're "
        f"not delivering measurable value, you're free to walk away with "
        f"no long-term lock-in.</p>"
        f"<p>We'd rather earn your business every month than trap you in a "
        f"contract you're unhappy with.</p>"),
    "product": lambda name: ("Try It Risk-Free",
        f"<p>{name} includes a free trial, and you can cancel your "
        f"subscription anytime — no long-term contracts, no hassle.</p>"
        f"<p>Cancel in a couple of clicks from your account settings, no "
        f"support ticket or phone call required.</p>"),
    "betting": lambda name: ("Our Player Protection Promise",
        f"<p>{name} is built on secure, licensed infrastructure — your funds "
        f"and personal data are protected, and every market is priced "
        f"fairly. We also provide tools to help you set deposit limits and "
        f"take a break whenever you need one.</p>"
        f"<p>Responsible play tools are built directly into your account "
        f"settings, not buried behind a support request.</p>"),
}


GUARANTEE_BULLETS = {
    "supplement": ["No complicated forms", "Fast, friendly support", "Full or partial refund options"],
    "education": ["No awkward exit interviews", "Refund processed quickly", "Keep any certificates already earned"],
    "business": ["Cancel with 30 days notice", "No hidden termination fees", "Data handed back on request"],
    "product": ["Cancel in one click", "No cancellation fees", "Export your data anytime"],
    "betting": ["Licensed & regulated platform", "Deposit limit & self-exclusion tools", "24/7 secure support"],
}


def _guarantee(cfg):
    name = cfg["product_name"]
    title, body = GUARANTEE_COPY.get(cfg["site_type"], GUARANTEE_COPY["product"])(name)
    return {
        "id": "guarantee", "layout": "guarantee",
        "title": title, "body": body,
        "bullets": GUARANTEE_BULLETS.get(cfg["site_type"], GUARANTEE_BULLETS["product"]),
        "image": _img("guarantee", f"{name} guarantee badge", 400, 400),
    }


# =======================================================================
# STATS
# =======================================================================
def _stats(cfg):
    rating = cfg["rating"]
    labels = {
        "supplement": ("Social Proof", "Trusted By Thousands"),
        "education": ("Social Proof", "Trusted By Students Everywhere"),
        "business": ("Track Record", "Results That Speak for Themselves"),
        "product": ("Social Proof", "Trusted By Teams Everywhere"),
        "betting": ("Social Proof", "Trusted By Players Everywhere"),
    }
    eyebrow, title = labels.get(cfg["site_type"], labels["product"])
    items = {
        "supplement": [
            {"number": rating["count"], "label": "Happy Customers"},
            {"number": f"{rating['value']}/5", "label": "Average Rating"},
            {"number": "30-Day", "label": "Money-Back Guarantee"},
            {"number": "100%", "label": "Transparent Ingredients"},
        ],
        "education": [
            {"number": rating["count"], "label": "Students Enrolled"},
            {"number": f"{rating['value']}/5", "label": "Average Rating"},
            {"number": "Lifetime", "label": "Access"},
            {"number": "100%", "label": "Self-Paced"},
        ],
        "business": [
            {"number": rating["count"], "label": "Clients Served"},
            {"number": f"{rating['value']}/5", "label": "Client Rating"},
            {"number": "5+", "label": "Years in Business"},
            {"number": "24/7", "label": "Support"},
        ],
        "product": [
            {"number": rating["count"], "label": "Active Users"},
            {"number": f"{rating['value']}/5", "label": "Average Rating"},
            {"number": "99.9%", "label": "Uptime"},
            {"number": "24/7", "label": "Support"},
        ],
        "betting": [
            {"number": rating["count"], "label": "Active Players"},
            {"number": f"{rating['value']}/5", "label": "Average Rating"},
            {"number": "24/7", "label": "Support"},
            {"number": "100%", "label": "Licensed & Secure"},
        ],
    }
    stat_items = items.get(cfg["site_type"], items["product"])[:]
    random.shuffle(stat_items)
    return {"id": "stats", "layout": "stats", "eyebrow": eyebrow, "title": title,
            "items": stat_items}


# =======================================================================
# TESTIMONIALS
# =======================================================================
def _testimonials(cfg):
    labels = {
        "supplement": ("Real Feedback", "What Customers Are Saying", "Customer"),
        "education": ("Student Results", "What Students Are Saying", "Student"),
        "business": ("Client Results", "What Clients Are Saying", "Client"),
        "product": ("Loved by Users", "What Users Are Saying", "User"),
        "betting": ("Player Reviews", "What Players Are Saying", "Player"),
    }
    eyebrow, title, kind = labels.get(cfg["site_type"], labels["product"])
    real = cfg.get("testimonials_data") or []

    if real:
        target_count = max(3, len(real[:6]))  # always at least 3 columns
        items = []
        for i in range(target_count):
            if i < len(real):
                quote = real[i].get("quote", "").strip() or f"Replace with a real, verified {kind.lower()} testimonial."
                person_name = real[i].get("name", "").strip() or f"Verified {kind}"
                role = real[i].get("role", "").strip() or "Replace with real name"
            else:
                quote = f"Replace with a real, verified {kind.lower()} testimonial."
                person_name = f"Verified {kind}"
                role = "Replace with real name"
            items.append({
                "quote": quote, "name": person_name, "role": role,
                "avatar": _img(f"customer-review-{i + 1}", f"{person_name} avatar", 200, 200),
            })
    else:
        # 3 columns by default (not 2) even for placeholders, so the
        # section always renders a proper 3-up grid.
        items = [
            {"quote": f"Replace with a real, verified {kind.lower()} testimonial.",
             "name": f"Verified {kind}", "role": "Replace with real name",
             "avatar": _img(f"customer-review-{i + 1}", f"{kind} avatar {i + 1}", 200, 200)}
            for i in range(3)
        ]

    intro_body = {
        "supplement": f"<p>Don't just take our word for it — here's what real customers say after adding {cfg['product_name']} to their routine.</p>",
        "education": f"<p>Don't just take our word for it — here's what real students say after taking {cfg['product_name']}.</p>",
        "business": f"<p>Don't just take our word for it — here's what real clients say about working with {cfg['product_name']}.</p>",
        "product": f"<p>Don't just take our word for it — here's what real users say about {cfg['product_name']}.</p>",
        "betting": f"<p>Don't just take our word for it — here's what real players say about {cfg['product_name']}.</p>",
    }
    return {"id": "testimonials", "layout": "testimonials", "eyebrow": eyebrow, "title": title,
            "body": intro_body.get(cfg["site_type"], intro_body["product"]), "items": items}


# =======================================================================
# PRICING
# =======================================================================
def _pricing(cfg):
    price = cfg["price"]
    name = cfg["product_name"]
    plans = {
        "supplement": ("Choose Your Package", f"Get {name} Today", "/ bottle", [
            ("1 Bottle", ["30-day supply", "Standard shipping", "30-day guarantee"], "Select", False, "product-1-bottle"),
            ("3 Bottles", ["90-day supply", "Free shipping", "30-day guarantee", "Best for full cycle"], "Most Popular", True, "product-3-bottles"),
            ("6 Bottles", ["180-day supply", "Free priority shipping", "30-day guarantee", "Lowest price per bottle"], "Best Value", False, "product-6-bottles"),
        ]),
        "education": ("Enrollment", f"Join {name}", "one-time", [
            ("Self-Paced", ["Lifetime access", "All modules", "Community access"], "Enroll", False, "product-1-bottle"),
            ("Guided Cohort", ["Everything in Self-Paced", "Live Q&A sessions", "Feedback on projects", "Certificate of completion"], "Most Popular", True, "product-3-bottles"),
            ("1:1 Mentorship", ["Everything in Guided", "1:1 mentor calls", "Resume/portfolio review", "Priority support"], "Best Value", False, "product-6-bottles"),
        ]),
        "business": ("Pricing", "Simple, Transparent Plans", "/ month", [
            ("Starter", ["Core service", "Monthly reporting", "Email support"], "Get Started", False, "product-1-bottle"),
            ("Growth", ["Everything in Starter", "Priority support", "Weekly reporting", "Strategy calls"], "Most Popular", True, "product-3-bottles"),
            ("Enterprise", ["Everything in Growth", "Dedicated account manager", "Custom reporting", "SLA guarantee"], "Contact Sales", False, "product-6-bottles"),
        ]),
        "product": ("Pricing", "Simple Plans for Every Team", "/ month", [
            ("Starter", ["Core features", "1 user", "Email support"], "Start Free Trial", False, "product-1-bottle"),
            ("Pro", ["Everything in Starter", "Up to 10 users", "Priority support", "Advanced features"], "Most Popular", True, "product-3-bottles"),
            ("Enterprise", ["Everything in Pro", "Unlimited users", "Dedicated support", "Custom integrations"], "Contact Sales", False, "product-6-bottles"),
        ]),
        "betting": ("Welcome Bonuses", "Choose Your Welcome Bonus", "bonus", [
            ("Starter Bonus", ["Matched deposit bonus", "Access to all markets", "Standard support"], "Claim Bonus", False, "product-1-bottle"),
            ("Popular Bonus", ["Higher deposit match", "Free bet credits included", "Priority support"], "Most Popular", True, "product-3-bottles"),
            ("VIP Bonus", ["Maximum deposit match", "VIP account manager", "Exclusive odds boosts"], "Claim Bonus", False, "product-6-bottles"),
        ]),
    }
    eyebrow, title, period, tiers = plans.get(cfg["site_type"], plans["product"])
    price_keys = ["one_bottle", "three_bottle_each", "six_bottle_each"]
    custom_labels = cfg.get("tier_labels") or []
    items = [
        {"name": (custom_labels[i] if i < len(custom_labels) and custom_labels[i] else tname),
         "price": price[price_keys[i]], "period": period,
         "features": feats, "cta_label": cta_label, "highlighted": highlighted,
         "image": _img(img_suffix, f"{custom_labels[i] if i < len(custom_labels) and custom_labels[i] else tname} plan", 1000, 900)}
        for i, (tname, feats, cta_label, highlighted, img_suffix) in enumerate(tiers)
    ]
    intro_body = {
        "supplement": f"<p>Pick the package that fits how long you're planning to stick with {name} — most customers choose a multi-bottle bundle to lock in the lowest price per bottle.</p>",
        "education": f"<p>Pick the plan that matches how much guidance you want along the way — from fully self-paced to hands-on mentorship.</p>",
        "business": f"<p>Pick the plan that matches your current scope — you can always move up as your needs grow.</p>",
        "product": f"<p>Pick the plan that matches your team's size today — upgrading later takes just a couple of clicks.</p>",
        "betting": f"<p>Pick the welcome bonus tier that matches how you plan to play — bigger deposits unlock bigger matched bonuses.</p>",
    }
    return {"id": "pricing", "layout": "pricing", "eyebrow": eyebrow, "title": title,
            "body": intro_body.get(cfg["site_type"], intro_body["product"]), "items": items}


# =======================================================================
# POST-PURCHASE ("What happens after you click Buy Now?")
# =======================================================================
def _post_purchase(cfg):
    cta_label = cfg.get("cta_label", "Buy Now")
    items = {
        "supplement": [
            {"number": "1", "title": "Secure Checkout", "text": "Your order is processed through an encrypted, secure checkout."},
            {"number": "2", "title": "Order Confirmation", "text": "You'll get an email confirming your order and package."},
            {"number": "3", "title": "Fast Shipping", "text": "Your order ships within 1-2 business days with tracking."},
            {"number": "4", "title": "Start Your Routine", "text": "Follow the label directions and stay consistent for best results."},
        ],
        "education": [
            {"number": "1", "title": "Secure Checkout", "text": "Your enrollment is processed through encrypted checkout."},
            {"number": "2", "title": "Instant Access", "text": "You'll receive login details by email right away."},
            {"number": "3", "title": "Start Learning", "text": "Jump into Module 1 whenever you're ready."},
            {"number": "4", "title": "Get Support", "text": "Reach out anytime if you have questions along the way."},
        ],
        "business": [
            {"number": "1", "title": "We Reach Out", "text": "Our team follows up within one business day to schedule your consultation."},
            {"number": "2", "title": "Discovery Call", "text": "We learn about your goals and current situation."},
            {"number": "3", "title": "Proposal", "text": "You receive a clear, custom plan and pricing."},
            {"number": "4", "title": "Kickoff", "text": "Once approved, we get to work."},
        ],
        "product": [
            {"number": "1", "title": "Instant Access", "text": "Your account is ready the moment you sign up."},
            {"number": "2", "title": "Welcome Email", "text": "You'll get a quick-start guide by email."},
            {"number": "3", "title": "Onboarding", "text": "Set up your workspace in a few minutes."},
            {"number": "4", "title": "You're Live", "text": "Start using it with your team right away."},
        ],
        "betting": [
            {"number": "1", "title": "Account Verification", "text": "Confirm your age and identity to activate your account."},
            {"number": "2", "title": "Bonus Applied", "text": "Your welcome bonus is credited after your first qualifying deposit."},
            {"number": "3", "title": "Explore Markets", "text": "Browse live odds and upcoming events."},
            {"number": "4", "title": "Place Your First Bet", "text": "Confirm your wager and track it in real time."},
        ],
    }
    return {
        "id": "post_purchase", "layout": "steps",
        "eyebrow": "What Happens Next",
        "title": f'What Happens After You Click "{cta_label}"?',
        "items": items.get(cfg["site_type"], items["product"]),
    }


# =======================================================================
# URGENCY ("Don't Wait Any Longer!")
# =======================================================================
def _urgency(cfg):
    name = cfg["product_name"]
    cta_label = cfg.get("cta_label", "Order Now")
    body = {
        "supplement": (
            f"<p>This discounted pricing on {name} won't last — multi-bottle "
            f"bundles are limited and pricing can change without notice.</p>"
            f"<p>Lock in your savings today rather than paying full price "
            f"later once the current offer ends.</p>"
        ),
        "education": (
            f"<p>Enrollment pricing for {name} is subject to change as new "
            f"modules are added to the curriculum.</p>"
            f"<p>Enroll now to lock in today's price before the course "
            f"expands and pricing adjusts to match.</p>"
        ),
        "business": (
            f"<p>We only take on a limited number of new clients each month "
            f"to protect the quality of our work for everyone we serve.</p>"
            f"<p>Book your free consultation before spots fill up for this "
            f"month's intake.</p>"
        ),
        "product": (
            f"<p>Introductory pricing for {name} won't be around forever — "
            f"rates typically increase as new features roll out.</p>"
            f"<p>Start your free trial today and lock in your rate before "
            f"that happens.</p>"
        ),
        "betting": (
            f"<p>Welcome bonus terms for {name} can change at any time as "
            f"promotions rotate throughout the year.</p>"
            f"<p>Sign up today to lock in the current offer before it's "
            f"replaced with a different one.</p>"
        ),
    }
    return {
        "id": "urgency", "layout": "urgency",
        "title": "Don't Wait Any Longer!",
        "body": body.get(cfg["site_type"], body["product"]),
        "image": _img("discount", "Limited-time discount badge", 400, 400),
        "cta": {"label": cta_label, "href": cfg["affiliate_link"]},
    }


# =======================================================================
# USAGE ("How to Use: Usage, Dosage & Directions") - supplement only
# =======================================================================
def _usage(cfg):
    if cfg["site_type"] != "supplement":
        return None
    name = cfg["product_name"]
    body = (
        f"<p>Getting the most out of {name} comes down to using it the same "
        f"way, every day — consistency matters far more than any single "
        f"dose.</p>"
        f"<p>Follow the exact directions printed on your label — including "
        f"the recommended amount and how often to take it — since it's "
        f"formulated to that specific dosage.</p>"
        f"<p>Most people find it easiest to pair it with an existing daily "
        f"habit, like breakfast or their morning routine, so it never gets "
        f"forgotten or skipped.</p>"
        f"<p>Store it as directed on the label (typically a cool, dry place "
        f"out of direct sunlight) to help preserve potency until you finish "
        f"the bottle.</p>"
        f"<p>If you're pregnant, nursing, taking medication, or managing a "
        f"health condition, talk to your doctor before starting — the "
        f"directions on the label are general guidance, not personalized "
        f"medical advice.</p>"
    )
    return {
        "id": "usage", "layout": "text", "align_left": True,
        "full_width": True, "columns": True,
        "eyebrow": "Directions", "title": f"How to Use {name}: Usage, Dosage &amp; Directions",
        "body": body,
        "bullets": ["Follow label directions exactly", "Take at the same time daily",
                    "Store in a cool, dry place", "Consult a doctor if unsure"],
    }


# =======================================================================
# PROS & CONS
# =======================================================================
def _pros_cons(cfg):
    name = cfg["product_name"]
    data = {
        "supplement": {
            "pros": ["Clearly labeled ingredients, no proprietary blend guesswork",
                     "Simple one-serving daily routine", "Backed by a money-back guarantee",
                     "Ships discreetly with tracking included"],
            "cons": ["Results build gradually, not overnight", "Only available online, not in retail stores",
                     "Requires daily consistency to see results"],
        },
        "education": {
            "pros": ["Learn at your own pace, no fixed schedule", "Real projects, not just theory",
                     "Lifetime access to revisit any lesson", "Certificate on completion"],
            "cons": ["Requires self-discipline to finish", "No in-person classroom setting",
                     "Best results take real practice time, not just watching"],
        },
        "business": {
            "pros": ["Custom plan, not a templated package", "Transparent, plain-English reporting",
                     "Direct access to your actual team", "Flexible terms, no long-term lock-in"],
            "cons": ["Results depend on your industry and starting point", "Requires some time investment on your end",
                     "Not a fit for businesses wanting the cheapest option available"],
        },
        "product": {
            "pros": ["Fast setup, no steep learning curve", "Works with tools you already use",
                     "Scales from solo use to full teams", "Cancel anytime, no long contracts"],
            "cons": ["Some advanced features are on higher tiers", "Best value comes with team, not solo, use",
                     "Requires an internet connection to use"],
        },
        "betting": {
            "pros": ["Licensed and regulated platform", "Fast payouts, not held up for days",
                     "Competitive odds across markets", "Responsible-play tools built in"],
            "cons": ["Availability depends on your local jurisdiction", "Bonus terms have wagering requirements",
                     "Like all betting, outcomes are never guaranteed"],
        },
    }
    d = data.get(cfg["site_type"], data["product"])
    return {
        "id": "pros_cons", "layout": "pros_cons",
        "eyebrow": "An Honest Look", "title": f"{name}: Pros &amp; Cons",
        "body": f"<p>No product is perfect for everyone — here's a balanced, honest look at {name} so you can decide if it's right for you.</p>",
        "pros": d["pros"], "cons": d["cons"],
    }


# =======================================================================
# FREE BONUSES
# =======================================================================
def _bonuses(cfg):
    name = cfg["product_name"]
    data = {
        "supplement": ("Free Bonuses With Your Order", [
            {"icon": "bi-truck", "title": "Free Fast Shipping", "text": "No extra shipping fees on qualifying multi-bottle orders."},
            {"icon": "bi-journal-text", "title": "Free Usage Guide", "text": "A simple digital guide covering dosage tips and best practices."},
            {"icon": "bi-headset", "title": "Free Priority Support", "text": "Direct access to our support team for any questions."},
        ]),
        "education": ("Free Bonuses With Enrollment", [
            {"icon": "bi-file-earmark-text", "title": "Free Resource Pack", "text": "Templates and cheat sheets to go along with the lessons."},
            {"icon": "bi-people", "title": "Free Community Access", "text": "Join fellow students for support and accountability."},
            {"icon": "bi-award", "title": "Free Certificate", "text": "Included at no extra cost when you complete the course."},
        ]),
        "business": ("What's Included at No Extra Cost", [
            {"icon": "bi-graph-up", "title": "Free Strategy Session", "text": "A complimentary planning call before work begins."},
            {"icon": "bi-file-earmark-bar-graph", "title": "Free Monthly Reporting", "text": "Plain-English performance reports, included as standard."},
            {"icon": "bi-headset", "title": "Free Priority Support", "text": "Direct access to your account contact, no extra fee."},
        ]),
        "product": ("Free With Every Plan", [
            {"icon": "bi-cloud-arrow-up", "title": "Free Onboarding", "text": "Guided setup to get your team running quickly."},
            {"icon": "bi-file-earmark-text", "title": "Free Templates", "text": "A starter set of templates to help you get going faster."},
            {"icon": "bi-headset", "title": "Free Support", "text": "Included support with every plan, no add-on fee."},
        ]),
        "betting": ("Free Bonuses for New Players", [
            {"icon": "bi-gift", "title": "Free Bet Credit", "text": "Bonus bet credit included with your first qualifying deposit."},
            {"icon": "bi-journal-text", "title": "Free Betting Guide", "text": "A quick-start guide to markets, odds, and placing your first bet."},
            {"icon": "bi-headset", "title": "Free VIP Support", "text": "Priority support access for new players getting started."},
        ]),
    }
    title, items = data.get(cfg["site_type"], data["product"])
    return {
        "id": "bonuses", "layout": "grid",
        "eyebrow": "Free Bonuses", "title": title,
        "body": f"<p>Here's what you get on top of {name} itself — no hidden fees, no upsell required. (Customize these to match whatever bonuses you're actually offering.)</p>",
        "items": items,
    }


# =======================================================================
# FREE SHIPPING - supplement only
# =======================================================================
def _shipping(cfg):
    if cfg["site_type"] != "supplement":
        return None
    name = cfg["product_name"]
    body = (
        f"<p>Every {name} order ships with free standard shipping on "
        f"qualifying multi-bottle packages — no surprise fees added at "
        f"checkout.</p>"
        f"<p>Orders are typically processed within 1-2 business days, and "
        f"you'll receive a confirmation email with tracking as soon as "
        f"your package ships.</p>"
        f"<p>Packaging is discreet, so what arrives at your door doesn't "
        f"announce what's inside to anyone else handling your mail.</p>"
    )
    return {
        "id": "shipping", "layout": "text",
        "eyebrow": "Free Shipping", "title": "Fast, Free Shipping on Your Order",
        "body": body,
        "bullets": ["Free shipping on multi-bottle orders", "1-2 business day processing", "Tracking included", "Discreet packaging"],
    }


# =======================================================================
# WHERE TO BUY - supplement + betting
# =======================================================================
def _where_to_buy(cfg):
    if cfg["site_type"] not in ("supplement", "betting"):
        return None
    name = cfg["product_name"]
    cta_label = cfg.get("cta_label", "Buy Now")
    if cfg["site_type"] == "supplement":
        body = (
            f"<p>To avoid counterfeit or expired stock, only purchase "
            f"{name} through the official website — not third-party "
            f"marketplaces or resellers you don't recognize.</p>"
            f"<p>Buying direct also means you're covered by our guarantee "
            f"and get accurate, fresh inventory shipped straight from our "
            f"fulfillment center.</p>"
        )
    else:
        body = (
            f"<p>Only use {name}'s official site or app to sign up and "
            f"deposit — never a third-party link claiming to offer better "
            f"odds or bonuses.</p>"
            f"<p>Signing up directly is the only way to guarantee your "
            f"account, bonus, and funds are properly protected under our "
            f"licensing.</p>"
        )
    return {
        "id": "where_to_buy", "layout": "text",
        "eyebrow": "Where to Buy", "title": f"Where to Buy {name}",
        "body": body,
        "cta": {"label": cta_label, "href": cfg["affiliate_link"]},
    }


# =======================================================================
# FAQ (placeholder section; actual Q&A pulled from seo.py FAQS_BY_TYPE)
# =======================================================================
def _faq(cfg):
    return {"id": "faq", "layout": "faq", "eyebrow": "Questions", "title": "Frequently Asked Questions"}


# =======================================================================
# CONCLUSION
# =======================================================================
def _conclusion(cfg):
    name, cat = cfg["product_name"], cfg["category"]
    body = {
        "supplement": (
            f"<p>If you've been searching for a straightforward, transparent "
            f"{_safe_keyword(cfg)}, {name} is worth a closer look.</p>"
            f"<p>Explore the packages above and choose the option that fits "
            f"your goals and your budget.</p>"
        ),
        "education": (
            f"<p>{name} gives you a clear, practical path into {cat.lower()} "
            f"— no guesswork, no wasted time on filler content.</p>"
            f"<p>Enroll today and start building real skills you can actually "
            f"apply.</p>"
        ),
        "business": (
            f"<p>{name} is built for businesses who want a real partner, not "
            f"just another vendor sending monthly invoices.</p>"
            f"<p>Book a free consultation and see what's actually possible "
            f"for your specific situation.</p>"
        ),
        "product": (
            f"<p>{name} takes the busywork out of {cat.lower()} so you can "
            f"focus on what actually matters for your team.</p>"
            f"<p>Start your free trial today — no credit card, no long-term "
            f"commitment required.</p>"
        ),
        "betting": (
            f"<p>{name} is built for players who want fair odds, fast "
            f"payouts, and a platform they can genuinely trust.</p>"
            f"<p>Sign up today and claim your welcome bonus before the "
            f"current offer changes.</p>"
        ),
    }
    return {"id": "conclusion", "layout": "text", "title": "Final Thoughts",
            "show_in_nav": False, "body": body.get(cfg["site_type"], body["product"])}


# =======================================================================
# CTA (mandatory, last)
# =======================================================================
CTA_COPY = {
    "supplement": lambda cfg: ("Ready to Get Started?",
        f"<p>Join the customers who chose {cfg['product_name']} for their {cfg['category'].lower()} routine today.</p>",
        f"Order {cfg['product_name']} Today"),
    "education": lambda cfg: ("Ready to Start Learning?",
        f"<p>Enroll in {cfg['product_name']} today and start building real {cfg['category'].lower()} skills.</p>",
        "Enroll Now"),
    "business": lambda cfg: ("Let's Talk About Your Project",
        f"<p>Book a free consultation with {cfg['product_name']} and see what's possible.</p>",
        "Get a Free Consultation"),
    "product": lambda cfg: ("Ready to Try It?",
        f"<p>Start your free trial of {cfg['product_name']} today — no credit card required.</p>",
        "Start Free Trial"),
    "betting": lambda cfg: ("Ready to Play?",
        f"<p>Join {cfg['product_name']} today and claim your welcome bonus.</p>",
        "Claim Your Bonus"),
}


def _cta(cfg):
    title, body, label = CTA_COPY.get(cfg["site_type"], CTA_COPY["product"])(cfg)
    return {
        "id": "cta", "layout": "cta", "theme": "brand",
        "title": title, "body": body,
        "cta": {"label": label, "href": cfg["affiliate_link"]},
    }


BUILDERS = {
    "intro": _intro, "what_is": _what_is, "why_choose": _why_choose,
    "how_it_works": _how_it_works, "usage": _usage, "benefits": _benefits,
    "pros_cons": _pros_cons, "ingredients": _ingredients,
    "guarantee": _guarantee, "bonuses": _bonuses, "shipping": _shipping,
    "stats": _stats, "testimonials": _testimonials,
    "pricing": _pricing, "post_purchase": _post_purchase, "urgency": _urgency,
    "where_to_buy": _where_to_buy,
    "faq": _faq, "conclusion": _conclusion,
}


# Zoned randomization: sections in the same zone get shuffled relative to
# each other on every generation (so no two generated pages share the same
# structure), but the zones themselves stay in this relative order so the
# page still reads as a coherent persuasive arc: hook -> explain -> convince
# -> price -> handle objections -> close. Fully unconstrained shuffling
# would just as often put FAQ before the product is even explained, or
# Pricing before any benefit is stated -- worse for conversion and no more
# "unique" than zoned shuffling for SEO/structural-fingerprint purposes.
OPENING_ZONE = ["intro", "what_is"]
MIDDLE_ZONE = ["why_choose", "how_it_works", "usage", "benefits", "pros_cons",
               "ingredients", "guarantee", "bonuses", "shipping", "stats",
               "testimonials", "post_purchase", "urgency"]
CLOSING_ZONE = ["pricing", "where_to_buy", "faq"]  # conclusion is pinned separately below - always last


def build_sections(cfg):
    site_type = cfg.get("site_type", "product")
    available = AVAILABLE_BY_TYPE.get(site_type, AVAILABLE_BY_TYPE["product"])
    requested = cfg.get("selected_sections") or DEFAULT_SELECTED.get(site_type, available)
    requested_ordered = [sid for sid in requested if sid in available]
    chosen = set(requested_ordered)

    if cfg.get("randomize_section_order", True):
        opening = [sid for sid in OPENING_ZONE if sid in chosen]
        middle = [sid for sid in MIDDLE_ZONE if sid in chosen]
        closing = [sid for sid in CLOSING_ZONE if sid in chosen]
        random.shuffle(opening)
        random.shuffle(middle)
        random.shuffle(closing)
        selected = opening + middle + closing
        # Conclusion always comes last among the content sections (right
        # before the mandatory final CTA) -- it's a closing summary, so
        # it should never end up shuffled ahead of Pricing/FAQ.
        if "conclusion" in chosen:
            selected.append("conclusion")
    else:
        # Manual mode: respect the exact order sections were submitted in
        # (the wizard's up/down reorder controls change this order directly).
        selected = requested_ordered

    sections = [_hero(cfg)]
    alt_toggle = False
    for sid in selected:
        fn = BUILDERS.get(sid)
        if not fn:
            continue
        sec = fn(cfg)
        if not sec:
            continue
        if sid in FORCED_THEME:
            sec["theme"] = FORCED_THEME[sid]
        else:
            sec.setdefault("theme", "alt" if alt_toggle else "light")
            alt_toggle = not alt_toggle
        if "show_in_nav" not in sec:
            sec["show_in_nav"] = sid in NAV_CANDIDATES
        if sec["show_in_nav"] and sid in NAV_LABELS:
            sec["nav_label"] = NAV_LABELS[sid]
        sections.append(sec)
    sections.append(_cta(cfg))
    return sections
