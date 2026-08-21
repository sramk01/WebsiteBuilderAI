"""
seo.py
------
Builds all SEO-related data: meta tags, JSON-LD schema blocks,
sitemap.xml, robots.txt.
"""

import json
from datetime import date

FAQS_BY_TYPE = {
    "supplement": [
        ("Is {name} safe to use?",
         "{name} is formulated with clearly labeled ingredients. As with any "
         "supplement, consult your doctor before use, especially if pregnant, "
         "nursing, or managing a medical condition."),
        ("How long until I see results?",
         "Individual results vary. Most customers are advised to use {name} "
         "consistently for 60-90 days to give the formula a full cycle."),
        ("Where can I buy {name}?",
         "To avoid counterfeit products, only purchase {name} through the "
         "official website linked on this page."),
        ("Is there a money-back guarantee?",
         "Yes. {name} is backed by a satisfaction guarantee — see our Refund "
         "Policy page for full details and timelines."),
        ("Are there any side effects?",
         "{name} is made with everyday ingredients, but individual sensitivity "
         "varies. Discontinue use and consult a doctor if you experience any "
         "adverse reaction."),
    ],
    "education": [
        ("Do I need prior experience to enroll in {name}?",
         "No. {name} is built to take you from the basics through to "
         "applied, real-world projects."),
        ("How long do I have access to {name}?",
         "You get lifetime access, so you can revisit lessons anytime and "
         "learn at your own pace."),
        ("Is there a certificate on completion?",
         "Yes, you'll receive a certificate of completion once you finish "
         "all modules of {name}."),
        ("Is there support if I get stuck?",
         "Yes — depending on your plan you'll have access to community "
         "support, Q&A sessions, or 1:1 mentorship."),
        ("Is there a refund policy?",
         "Yes, see our Refund Policy page for the full terms and timelines."),
    ],
    "business": [
        ("What does {name} actually do for clients?",
         "{name} provides a clear strategy, hands-on execution, and "
         "transparent reporting tailored to your goals."),
        ("How long are your contracts?",
         "We keep terms flexible — see our Terms & Conditions page for "
         "current contract details."),
        ("How is pricing structured?",
         "Pricing is tiered by scope of work; see the Pricing section above "
         "or contact us for a custom quote."),
        ("Do you work with businesses in my industry?",
         "{name} has worked across a range of industries — reach out and "
         "we'll tell you honestly if we're a good fit."),
        ("How do we get started?",
         "Book a free consultation using the button on this page and we'll "
         "walk you through next steps."),
    ],
    "product": [
        ("Is there a free trial for {name}?",
         "Yes, {name} offers a free trial with no credit card required."),
        ("Can I cancel anytime?",
         "Yes, you can cancel your {name} subscription at any time from "
         "your account settings."),
        ("Does {name} integrate with other tools?",
         "Yes, {name} is built to connect with the tools you already use — "
         "see the Features section above."),
        ("Is my data secure with {name}?",
         "Yes, {name} uses end-to-end encryption and follows industry "
         "standard security practices."),
        ("What support is included?",
         "All {name} plans include support; higher tiers include priority "
         "and dedicated support."),
    ],
    "betting": [
        ("Is {name} safe and legal to use?",
         "{name} operates under proper licensing and uses industry-standard "
         "security to protect your funds and personal data. You must meet "
         "the minimum legal gambling age in your jurisdiction to sign up."),
        ("How do I claim my welcome bonus?",
         "Sign up, verify your account, and make a qualifying deposit — "
         "your bonus is credited automatically per the terms shown at "
         "signup."),
        ("How long do withdrawals take?",
         "Withdrawal times vary by payment method, but {name} processes "
         "requests promptly — see the Shipping/Payout Policy page for "
         "typical timeframes."),
        ("What if I need to stop or take a break?",
         "{name} provides deposit limits, time-outs, and self-exclusion "
         "tools in your account settings — see our Responsible Gambling "
         "page for details and support resources."),
        ("What payment methods are supported?",
         "{name} supports a range of secure deposit and withdrawal "
         "methods — see the payments section of your account for the "
         "full list."),
    ],
}


def build_meta(cfg):
    name = cfg["product_name"]
    pk = cfg["primary_keyword"]
    sk = cfg.get("secondary_keywords", [])
    domain = cfg["domain"].rstrip("/")
    slug = cfg["_slug"]

    title = f"{name} | {pk.title()}"
    if len(title) > 60:
        title = title[:57] + "..."

    desc = (f"{name} is a premium {cfg['category'].lower()} formula. "
            f"Discover benefits, ingredients, pricing and real results.")
    if len(desc) > 160:
        desc = desc[:157] + "..."

    return {
        "title": title,
        "description": desc,
        "keywords": ", ".join([pk] + sk),
        "canonical": f"{domain}/",
        "og_url": f"{domain}/",
        "domain": domain,
        "slug": slug,
    }


def build_schema(cfg):
    name = cfg["product_name"]
    domain = cfg["domain"].rstrip("/")
    rating = cfg.get("rating", {"value": "4.8", "count": "100"})
    price = cfg.get("price", {})

    organization = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": cfg.get("business_name", name),
        "url": domain,
        "logo": f"{domain}/assets/images/{cfg['_slug']}-favicon.webp",
    }

    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": name,
        "url": domain,
    }

    site_type = cfg.get("site_type", "product")
    slug = cfg["_slug"]

    if site_type == "education":
        primary_schema = {
            "@context": "https://schema.org",
            "@type": "Course",
            "name": name,
            "description": f"{name} - an online course covering {cfg['category'].lower()}.",
            "provider": {"@type": "Organization", "name": cfg.get("business_name", name), "sameAs": domain},
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": rating.get("value", "4.8"),
                "reviewCount": rating.get("count", "100"),
            },
        }
    elif site_type == "business":
        primary_schema = {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": cfg["category"],
            "name": name,
            "provider": {"@type": "Organization", "name": cfg.get("business_name", name), "sameAs": domain},
            "areaServed": "Worldwide",
        }
    else:
        primary_schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "image": f"{domain}/assets/images/{slug}-product-main.webp",
            "description": f"{name} - premium {cfg['category'].lower()} product.",
            "brand": {"@type": "Brand", "name": cfg.get("business_name", name)},
            "offers": {
                "@type": "Offer",
                "url": cfg.get("official_website", domain),
                "priceCurrency": price.get("currency", "USD"),
                "price": price.get("one_bottle", "0"),
                "availability": "https://schema.org/InStock",
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": rating.get("value", "4.8"),
                "reviewCount": rating.get("count", "100"),
            },
        }

    faqs = FAQS_BY_TYPE.get(site_type, FAQS_BY_TYPE["product"])
    faq_entities = [
        {
            "@type": "Question",
            "name": q.format(name=name),
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a.format(name=name),
            },
        }
        for q, a in faqs
    ]
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_entities,
    }

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{domain}/"},
            {"@type": "ListItem", "position": 2, "name": cfg["category"], "item": f"{domain}/"},
            {"@type": "ListItem", "position": 3, "name": name, "item": f"{domain}/"},
        ],
    }

    return {
        "organization": json.dumps(organization, indent=2),
        "website": json.dumps(website, indent=2),
        "product": json.dumps(primary_schema, indent=2),
        "faq": json.dumps(faq, indent=2),
        "breadcrumb": json.dumps(breadcrumb, indent=2),
    }


def build_faqs(cfg):
    name = cfg["product_name"]
    site_type = cfg.get("site_type", "product")
    faqs = FAQS_BY_TYPE.get(site_type, FAQS_BY_TYPE["product"])
    return [(q.format(name=name), a.format(name=name)) for q, a in faqs]


def build_sitemap(cfg, skip_pages=None):
    skip_pages = skip_pages or set()
    domain = cfg["domain"].rstrip("/")
    today = date.today().isoformat()
    pages = [
        p for p in [
            "", "privacy-policy.html", "disclaimer.html",
            "affiliate-disclosure.html", "medical-disclaimer.html",
            "responsible-gambling.html",
            "terms-and-conditions.html", "shipping-policy.html",
            "refund-policy.html", "contact.html",
        ] if p not in skip_pages
    ]
    urls = "\n".join(
        f'  <url><loc>{domain}/{p}</loc><lastmod>{today}</lastmod>'
        f'<changefreq>weekly</changefreq><priority>{"1.0" if p == "" else "0.5"}</priority></url>'
        for p in pages
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )


def build_robots(cfg):
    domain = cfg["domain"].rstrip("/")
    return (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {domain}/sitemap.xml\n"
    )


def build_htaccess(cfg):
    """Standard, safe Apache config: force HTTPS, custom 404, gzip
    compression, browser caching, and directory-listing protection."""
    return (
        "# Generated by Landing Page Generator\n"
        "# Force HTTPS\n"
        "RewriteEngine On\n"
        "RewriteCond %{HTTPS} off\n"
        "RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]\n\n"
        "# Custom 404 page\n"
        "ErrorDocument 404 /404.html\n\n"
        "# Disable directory listing\n"
        "Options -Indexes\n\n"
        "# GZIP compression\n"
        "<IfModule mod_deflate.c>\n"
        "  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml\n"
        "</IfModule>\n\n"
        "# Browser caching\n"
        "<IfModule mod_expires.c>\n"
        "  ExpiresActive On\n"
        "  ExpiresByType image/webp \"access plus 1 year\"\n"
        "  ExpiresByType text/css \"access plus 1 month\"\n"
        "  ExpiresByType application/javascript \"access plus 1 month\"\n"
        "  ExpiresByType text/html \"access plus 0 seconds\"\n"
        "</IfModule>\n"
    )


def build_llms_txt(cfg, sections):
    """llms.txt (https://llmstxt.org) -- a plain-language, markdown
    summary of the site aimed at AI assistants/crawlers, separate from
    robots.txt which targets traditional search crawlers."""
    name = cfg["product_name"]
    domain = cfg["domain"].rstrip("/")
    summary = f"{name} — {cfg['category']}. Primary focus: {cfg['primary_keyword']}."

    section_lines = "\n".join(
        f"- {s['title']}" for s in sections
        if s.get("title") and s["id"] not in ("hero", "cta")
    )

    pages = [
        ("Home", "/"),
        ("Privacy Policy", "/privacy-policy.html"),
        ("Terms & Conditions", "/terms-and-conditions.html"),
        ("Contact", "/contact.html"),
    ]
    page_lines = "\n".join(f"- [{label}]({domain}{path})" for label, path in pages)

    return (
        f"# {name}\n\n"
        f"> {summary}\n\n"
        f"## About\n"
        f"{name} is a {cfg['site_type']} landing page covering {cfg['category'].lower()}. "
        f"Business contact: {cfg['contact_email']}.\n\n"
        f"## Page Sections\n"
        f"{section_lines}\n\n"
        f"## Key Pages\n"
        f"{page_lines}\n"
    )
