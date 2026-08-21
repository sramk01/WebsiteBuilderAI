"""
wizard.py
---------
Interactive command-line wizard. Asks you a series of questions and
builds a config dict from your answers -- no manual JSON editing.

Run with:  python3 generate.py --interactive
"""

from site_content import SITE_TYPES

TYPE_LABELS = {
    "supplement": "Supplement / Health Product",
    "education": "Education / Online Course",
    "business": "Business / Agency / Services",
    "product": "Product / SaaS",
    "betting": "Betting / Gaming Platform",
}

TYPE_LINK_LABEL = {
    "supplement": "Official website / checkout URL",
    "education": "Enrollment URL",
    "business": "Contact / booking URL",
    "product": "Signup URL",
    "betting": "Signup / registration URL",
}


def ask(prompt, default=None, required=True):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        val = input(f"{prompt}{suffix}: ").strip()
        if not val and default is not None:
            return default
        if not val and not required:
            return ""
        if val:
            return val
        print("  This field is required.")


def ask_choice(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        choice = input(f"Choose 1-{len(options)}: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  Please enter a valid number.")


def ask_list(prompt, min_items=1):
    print(f"\n{prompt} (comma-separated)")
    while True:
        raw = input("> ").strip()
        items = [i.strip() for i in raw.split(",") if i.strip()]
        if len(items) >= min_items:
            return items
        print(f"  Please enter at least {min_items}.")


def run_wizard():
    print("=" * 60)
    print(" Landing Page Website Generator — Interactive Wizard")
    print("=" * 60)

    type_choice = ask_choice(
        "What kind of landing page do you want to build?",
        [TYPE_LABELS[t] for t in SITE_TYPES],
    )
    site_type = SITE_TYPES[[TYPE_LABELS[t] for t in SITE_TYPES].index(type_choice)]

    print(f"\n--- {TYPE_LABELS[site_type]} details ---")
    product_name = ask("Product / Course / Business name")
    category = ask("Category / field (e.g. 'Joint Support', 'Data Analytics', "
                    "'Digital Marketing', 'Project Management Software')")
    official_website = ask(f"{TYPE_LINK_LABEL[site_type]}")
    primary_keyword = ask("Primary SEO keyword")
    secondary_keywords = ask_list("Secondary SEO keywords", min_items=1)
    domain = ask("Your domain (e.g. https://www.yoursite.com)")
    business_name = ask("Business / brand name", default=product_name)
    contact_email = ask("Contact email", default=f"support@{domain.replace('https://', '').replace('http://', '')}")

    print("\n--- Pricing (3 tiers) ---")
    price_low = ask("Lowest tier price (number only)", default="49")
    price_mid = ask("Mid tier price (number only)", default="99")
    price_high = ask("Top tier price (number only)", default="199")
    currency = ask("Currency code", default="USD")

    print("\n--- Brand colors (hex, include #) ---")
    primary_color = ask("Primary color", default="#1F6F54")
    secondary_color = ask("Secondary/accent color", default="#F4A63E")
    dark_color = ask("Dark color (text/footer)", default="#123328")
    light_color = ask("Light color (backgrounds)", default="#FBF7EE")

    print("\n--- Social proof ---")
    rating_value = ask("Average rating out of 5", default="4.8")
    rating_count = ask("Number of reviews/customers", default="500")

    cfg = {
        "site_type": site_type,
        "product_name": product_name,
        "category": category,
        "official_website": official_website,
        "affiliate_link": official_website,
        "primary_keyword": primary_keyword,
        "secondary_keywords": secondary_keywords,
        "brand_colors": {
            "primary": primary_color,
            "secondary": secondary_color,
            "dark": dark_color,
            "light": light_color,
        },
        "domain": domain,
        "business_name": business_name,
        "contact_email": contact_email,
        "price": {
            "one_bottle": price_low,
            "three_bottle_each": price_mid,
            "six_bottle_each": price_high,
            "currency": currency,
        },
        "rating": {"value": rating_value, "count": rating_count},
        "use_ai_content": False,
    }

    print("\n✅ Config complete. Generating your site...\n")
    return cfg
