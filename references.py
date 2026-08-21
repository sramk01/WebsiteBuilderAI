"""
references.py
--------------
Step 15: "reference sites for analysis".

This does NOT scrape or copy competitor page content into the
generated site -- that would risk copyright infringement and produce
a site that's just a clone of someone else's copy. Instead, it builds
a private markdown notes file listing the URLs the user provided, with
(best-effort, gracefully-degrading) page title + meta description for
quick orientation, so the user has a starting point for their own
manual analysis.
"""

import re
import urllib.request
import urllib.error


def _fetch_title_and_description(url, timeout=5):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read(200_000).decode("utf-8", errors="ignore")
    except Exception:
        return None, None

    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else None

    desc_match = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        html, re.IGNORECASE,
    )
    description = re.sub(r"\s+", " ", desc_match.group(1)).strip() if desc_match else None

    return title, description


def build_reference_notes(cfg, urls):
    """Returns a markdown string listing each reference URL with a
    short, factual title/description where fetchable. Never includes
    body copy from the referenced pages."""
    if not urls:
        return None

    name = cfg["product_name"]
    lines = [
        f"# Competitive / Inspiration Notes for {name}\n",
        "These are reference sites you provided during generation. "
        "This file is for your own private research only -- none of "
        "this content was copied into your generated site. Use it as "
        "a starting point to note pricing, positioning, and messaging "
        "ideas in your own words.\n",
    ]

    for url in urls:
        url = url.strip()
        if not url:
            continue
        title, description = _fetch_title_and_description(url)
        lines.append(f"## {url}")
        if title:
            lines.append(f"- **Page title:** {title}")
        if description:
            lines.append(f"- **Meta description:** {description}")
        if not title and not description:
            lines.append("- _(Could not fetch page metadata -- check the site manually.)_")
        lines.append("- **Your notes:** _(add your own observations here)_\n")

    return "\n".join(lines)
