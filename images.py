"""
images.py
---------
Walks the section list (whatever site_type produced it) and collects
every declared image into one manifest, then renders placeholder
.webp files so the generated site never has a broken image.

Uploaded photos are used EXACTLY as provided by the user -- the only
operation ever applied is resizing/cropping to fit a section's layout
box. No background removal, no color changes, no other processing.

Replace the placeholders in assets/images/ with real photography
before going live. See manifest.json for exact suggested prompts.
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps


def save_uploaded_image(file_obj, target_path, w, h, crop_mode="cover"):
    """Takes an uploaded image (any format) and saves it as .webp at
    target_path, with NO changes of any kind to its colors, background,
    or content -- the only operation ever applied is the resize/crop
    needed to fit the target layout box, which is unavoidable for
    consistent page layout. Whatever background the photo has (black,
    white, transparent, anything) is preserved exactly as uploaded.

    crop_mode="cover" (default): crops to exactly fill w x h -- used for
    grid tiles (ingredients, pricing, avatars) where uniform framing
    across a row matters more than showing 100% of the original photo.

    crop_mode="contain": preserves the ENTIRE original image with no
    cropping, resized down to fit within w x h -- used for hero/banner
    and "what is" images, where cutting off the top/bottom of a user's
    photo (e.g. a product bottle) looks broken."""
    img = Image.open(file_obj)
    img = ImageOps.exif_transpose(img)  # respect phone camera orientation -- rotation only, never color/content
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    if crop_mode == "contain":
        # Only shrinks if larger than the target box; never crops, never
        # upscales, never adds a background behind the photo.
        img.thumbnail((w, h), Image.LANCZOS)
        result = img
    else:
        result = ImageOps.fit(img, (w, h), method=Image.LANCZOS, centering=(0.5, 0.5))

    # Preserve transparency if the original had it; otherwise plain RGB.
    # Either way, this is purely a format/mode conversion for saving --
    # it does not alter any pixel's color or add any background.
    if result.mode == "RGBA":
        # Only flatten to RGB if there's genuinely no transparency to keep
        alpha = result.getchannel("A")
        has_transparency = alpha.getextrema()[0] < 255
        if not has_transparency:
            result = result.convert("RGB")
        result.save(target_path, "WEBP", quality=90)
    else:
        result.save(target_path, "WEBP", quality=90)


def _entry(slug, spec, default_prompt):
    return {
        "filename": f"{slug}-{spec['suffix']}.webp",
        "size": f"{spec['w']}x{spec['h']}",
        "width": spec["w"],
        "height": spec["h"],
        "alt": spec["alt"],
        "title": spec["alt"],
        "prompt": spec.get("prompt", default_prompt),
    }


def collect_manifest(cfg, sections):
    """Walk every section + its items and collect all image specs."""
    slug = cfg["_slug"]
    manifest = []
    seen = set()

    def add(spec, default_prompt="Professional photo matching the section context"):
        if not spec:
            return
        key = spec["suffix"]
        if key in seen:
            return
        seen.add(key)
        manifest.append(_entry(slug, spec, default_prompt))

    # Always include favicon + social share images (used in <head> regardless
    # of which content sections are selected)
    add({"suffix": "favicon", "alt": f"{cfg['product_name']} logo favicon", "w": 512, "h": 512},
        "Minimal square logo icon")
    add({"suffix": "og-image", "alt": f"{cfg['product_name']} social share image", "w": 1200, "h": 630},
        "Wide social share graphic with product name and tagline")
    add({"suffix": "twitter-image", "alt": f"{cfg['product_name']} Twitter card image", "w": 1200, "h": 600},
        "Wide Twitter/X card graphic with product name and tagline")

    for sec in sections:
        add(sec.get("image"))
        add(sec.get("badge_image"))
        for item in sec.get("items", []):
            add(item.get("image"))
            add(item.get("avatar"), "Friendly headshot placeholder, neutral background")
            add(item.get("photo"), "Professional headshot, neutral background")

    return manifest


def _load_font(size):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
        )
    except Exception:
        return ImageFont.load_default()


def _hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def render_placeholders(manifest, out_dir, primary_hex="#1F6F54"):
    """Generates one plain white .webp placeholder per manifest entry --
    a simple picture-frame glyph on a solid white background, with NO
    color tint of any kind (not even a pale one). Never looks like an
    unwanted colored/black background, regardless of brand palette."""
    white = (255, 255, 255)
    line_color = (156, 163, 175)  # neutral gray, no brand-color tint at all

    for entry in manifest:
        w, h = entry["width"], entry["height"]
        img = Image.new("RGB", (w, h), color=white)
        draw = ImageDraw.Draw(img)

        # Subtle rounded "picture" glyph centered in the frame
        cx, cy = w / 2, h / 2
        icon_size = min(w, h) * 0.22
        box = [cx - icon_size, cy - icon_size * 0.75, cx + icon_size, cy + icon_size * 0.75]
        draw.rounded_rectangle(box, radius=icon_size * 0.15, outline=line_color, width=max(2, int(icon_size * 0.06)))
        # small "sun" circle
        sun_r = icon_size * 0.16
        draw.ellipse([cx - icon_size * 0.55, cy - icon_size * 0.4,
                      cx - icon_size * 0.55 + sun_r * 2, cy - icon_size * 0.4 + sun_r * 2],
                     outline=line_color, width=max(2, int(icon_size * 0.05)))
        # small "mountain" triangle
        draw.line([(cx - icon_size * 0.7, cy + icon_size * 0.55),
                    (cx - icon_size * 0.1, cy - icon_size * 0.05),
                    (cx + icon_size * 0.35, cy + icon_size * 0.3),
                    (cx + icon_size * 0.7, cy - icon_size * 0.1),
                    (cx + icon_size * 0.9, cy + icon_size * 0.55)],
                   fill=line_color, width=max(2, int(icon_size * 0.06)), joint="curve")

        label_font = _load_font(max(11, int(w // 30)))
        label = "Add your photo"
        bbox = draw.textbbox((0, 0), label, font=label_font)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) / 2, cy + icon_size * 0.95), label, fill=line_color, font=label_font)

        img.save(out_dir / entry["filename"], "WEBP", quality=85)
