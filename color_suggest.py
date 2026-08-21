"""
color_suggest.py
-----------------
Step 15 helper: "suggest a color from this reference site." Fetches
only the site's favicon (a small, publicly-intended-for-display icon,
not page content) and derives a full 4-color palette from its
dominant color -- never scrapes or reproduces any actual page content.

Gracefully returns None on any failure (no internet, no favicon found,
blocked, etc.) so the wizard can fall back to manual color pickers.
"""

import colorsys
import io
import re
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlparse

from PIL import Image


def _fetch(url, timeout=5):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _find_favicon_url(page_url):
    try:
        html = _fetch(page_url).decode("utf-8", errors="ignore")
    except Exception:
        html = ""

    match = re.search(
        r'<link[^>]+rel=["\'](?:shortcut )?icon["\'][^>]+href=["\']([^"\']+)["\']',
        html, re.IGNORECASE,
    )
    if match:
        return urljoin(page_url, match.group(1))

    parsed = urlparse(page_url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"


def _dominant_hex(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    img = img.resize((32, 32))
    pixels = [
        (r, g, b) for r, g, b, a in img.getdata()
        if a > 30 and not (r > 240 and g > 240 and b > 240)  # skip transparent/near-white
    ]
    if not pixels:
        return None
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return f"#{r:02x}{g:02x}{b:02x}"


def _hex_to_hsl(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return colorsys.rgb_to_hls(r, g, b)  # returns (h, l, s)


def _hsl_to_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, max(0, min(1, l)), max(0, min(1, s)))
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def derive_palette(primary_hex):
    """Given one primary color, derive a harmonious secondary/dark/light
    to complete the 4-color brand palette."""
    h, l, s = _hex_to_hsl(primary_hex)
    secondary = _hsl_to_hex((h + 0.5) % 1.0, min(0.6, l + 0.05), min(1, s * 0.9))  # complementary
    dark = _hsl_to_hex(h, max(0.12, l * 0.35), min(1, s * 1.1))
    light = _hsl_to_hex(h, 0.96, min(0.35, s * 0.4))
    return {"primary": primary_hex, "secondary": secondary, "dark": dark, "light": light}


def suggest_palette_from_url(url):
    """Best-effort: returns a derived 4-color palette dict, or None if
    anything fails (no internet, no favicon, unreadable image, etc.)."""
    try:
        favicon_url = _find_favicon_url(url)
        image_bytes = _fetch(favicon_url)
        dominant = _dominant_hex(image_bytes)
        if not dominant:
            return None
        return derive_palette(dominant)
    except Exception:
        return None
