#!/usr/bin/env python3
"""
app.py
------
Web front-end for the landing page generator.

Run:
    python3 app.py

Then open http://localhost:5000 in your browser. Fill in the
multi-step wizard, optionally upload a hero/main/feature image,
click Generate, and the browser downloads a ready-to-deploy .zip
of the site -- built by the exact same engine as the CLI tool
(generate.py / site_content.py / seo.py / images.py).

This is a single-user local/self-hosted app, not a hosted multi-tenant
SaaS (no accounts, billing, or persistent storage) -- see README.md
"Turning this into a hosted SaaS" section for what that next step
would involve.
"""

import json
import re
import shutil
import tempfile
import uuid
from pathlib import Path

import env_loader
env_loader.load_env_file()

from flask import Flask, request, send_file, jsonify, Response, send_from_directory

import generate as gen
import images as images_mod

app = Flask(__name__, static_folder="webui", static_url_path="")

JOBS_DIR = Path(tempfile.gettempdir()) / "webgen_jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/site-types")
def site_types():
    """Lets the frontend fetch valid site types + default CTA labels
    instead of hardcoding them twice."""
    import site_content
    return jsonify({
        "site_types": site_content.SITE_TYPES,
        "cta_labels": gen.DEFAULT_CTA_LABEL,
    })


@app.route("/api/templates")
def templates_catalog():
    """Returns selectable design templates for the wizard."""
    return jsonify({"templates": gen.get_template_catalog()})


@app.route("/api/preview-content", methods=["POST"])
def preview_content():
    """Builds generated section copy for the theme editor preview."""
    import site_content
    cfg = gen.validate_and_fill_config(_build_raw_config(request.form))
    sections = site_content.build_sections(cfg)
    custom = gen._custom_section_context(sections)
    custom["faq"]["items"] = gen._custom_faq_items(cfg, custom)

    def section(section_id):
        data = custom.get(section_id, {})
        return {
            "title": data.get("title", ""),
            "body": data.get("body", ""),
            "items": data.get("items", []),
        }

    return jsonify({
        "hero": section("hero"),
        "what_is": section("what_is"),
        "how_it_works": section("how_it_works"),
        "benefits": section("benefits"),
        "ingredients": section("ingredients"),
        "guarantee": section("guarantee"),
        "usage": section("usage"),
        "where_to_buy": section("where_to_buy"),
        "post_purchase": section("post_purchase"),
        "conclusion": section("conclusion"),
        "faq": section("faq"),
    })


@app.route("/template-assets/<template_id>/images/<path:filename>")
def template_image_asset(template_id, filename):
    """Serves bundled sample template images for the visual editor preview."""
    template = gen.CUSTOM_TEMPLATES.get(template_id)
    if not template:
        return Response("template not found", status=404)
    images_dir = Path(template["dir"]) / "assets" / "images"
    return send_from_directory(images_dir, filename)


@app.route("/api/ai-status")
def ai_status():
    """Reports server-side AI provider availability without exposing keys."""
    import os
    anthropic_has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    try:
        import anthropic  # noqa: F401
        anthropic_has_package = True
    except ImportError:
        anthropic_has_package = False
    openai_has_key = bool(os.environ.get("OPENAI_API_KEY"))
    try:
        import openai  # noqa: F401
        openai_has_package = True
    except ImportError:
        openai_has_package = False
    providers = {
        "anthropic": {
            "configured": anthropic_has_key and anthropic_has_package,
            "has_key": anthropic_has_key,
            "has_package": anthropic_has_package,
        },
        "openai": {
            "configured": openai_has_key and openai_has_package,
            "has_key": openai_has_key,
            "has_package": openai_has_package,
        },
    }
    return jsonify({"configured": any(p["configured"] for p in providers.values()),
                    "providers": providers})


@app.route("/api/sections")
def sections_catalog():
    """Returns the selectable section list (Step 13) for a given site type."""
    import site_content
    site_type = request.args.get("site_type", "product")
    if site_type not in site_content.SITE_TYPES:
        return jsonify({"error": "invalid site_type"}), 400
    return jsonify({"sections": site_content.get_section_catalog(site_type)})


@app.route("/api/suggest-colors")
def suggest_colors():
    """Best-effort: derives a 4-color palette from a reference site's
    favicon. Returns null if anything fails (no internet, no favicon,
    blocked, etc.) so the frontend can show a friendly fallback."""
    import color_suggest
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "url required"}), 400
    palette = color_suggest.suggest_palette_from_url(url)
    if not palette:
        return jsonify({"palette": None})
    return jsonify({"palette": palette})


def _build_raw_config(form):
    secondary = [k.strip() for k in form.get("secondary_keywords", "").split(",") if k.strip()]
    selected_sections = form.getlist("selected_sections") or None
    reference_sites = [
        u.strip() for u in re.split(r"[\n,]+", form.get("reference_sites", "")) if u.strip()
    ]

    ingredients_data = []
    for i in range(1, 11):
        ing_name = (form.get(f"ingredient_name_{i}") or "").strip()
        ing_desc = (form.get(f"ingredient_desc_{i}") or "").strip()
        if ing_name or ing_desc:
            ingredients_data.append({"name": ing_name, "description": ing_desc})

    testimonials_data = []
    for i in range(1, 7):
        quote = (form.get(f"testimonial_quote_{i}") or "").strip()
        person_name = (form.get(f"testimonial_name_{i}") or "").strip()
        role = (form.get(f"testimonial_role_{i}") or "").strip()
        if quote or person_name:
            testimonials_data.append({"quote": quote, "name": person_name, "role": role})

    theme_overrides = {}
    for key in [
        "header_brand", "header_nav_1", "header_nav_2", "header_nav_3", "header_nav_4", "header_cta",
        "hero_title", "hero_body", "what_title", "what_body",
        "how_title", "how_body", "benefits_title", "benefits_body",
        "ingredients_title", "ingredients_body", "usage_title", "usage_body",
        "where_title", "where_body", "guarantee_title", "guarantee_body",
        "post_purchase_title", "post_purchase_body",
        "conclusion_title", "conclusion_body", "footer_title", "footer_copyright",
    ]:
        value = (form.get(f"theme_{key}") or "").strip()
        if value:
            theme_overrides[key] = value

    faq_overrides = []
    for i in range(1, 7):
        q = (form.get(f"theme_faq_q_{i}") or "").strip()
        a = (form.get(f"theme_faq_a_{i}") or "").strip()
        if q or a:
            faq_overrides.append({"q": q, "a": a})
    if faq_overrides:
        theme_overrides["faq_items"] = faq_overrides

    return {
        "site_type": form.get("site_type", "product"),
        "product_name": form.get("product_name", "").strip(),
        "category": form.get("category", "").strip(),
        "official_website": form.get("official_website", "").strip(),
        "affiliate_link": form.get("official_website", "").strip(),
        "primary_keyword": form.get("primary_keyword", "").strip(),
        "secondary_keywords": secondary,
        "domain": form.get("domain", "").strip(),
        "business_name": (form.get("business_name") or form.get("product_name", "")).strip(),
        "contact_email": form.get("contact_email", "").strip(),
        "brand_colors": {
            "primary": form.get("color_primary") or "#1F6F54",
            "secondary": form.get("color_secondary") or "#F4A63E",
            "dark": form.get("color_dark") or "#123328",
            "light": form.get("color_light") or "#FBF7EE",
        },
        "price": {
            "one_bottle": form.get("price_low") or "49",
            "three_bottle_each": form.get("price_mid") or "99",
            "six_bottle_each": form.get("price_high") or "199",
            "currency": form.get("currency") or "USD",
        },
        "tier_labels": [
            (form.get("tier_label_1") or "").strip(),
            (form.get("tier_label_2") or "").strip(),
            (form.get("tier_label_3") or "").strip(),
        ],
        "rating": {
            "value": form.get("rating_value") or "4.8",
            "count": form.get("rating_count") or "500",
        },
        "template_id": form.get("template_id") or "default",
        "use_ai_content": form.get("use_ai_content") == "true",
        "fail_on_ai_error": form.get("use_ai_content") == "true",
        "ai_provider": form.get("ai_provider") or "anthropic",
        "anthropic_api_key": (form.get("anthropic_api_key") or "").strip() or None,
        "openai_api_key": (form.get("openai_api_key") or "").strip() or None,
        "selected_sections": selected_sections,
        "randomize_section_order": form.get("randomize_section_order") == "true",
        "reference_sites": reference_sites,
        "ingredients_data": ingredients_data,
        "testimonials_data": testimonials_data,
        "theme_overrides": theme_overrides,
    }


@app.route("/api/generate", methods=["POST"])
def api_generate():
    raw_cfg = _build_raw_config(request.form)

    try:
        cfg = gen.load_config_dict(raw_cfg)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    work_id = uuid.uuid4().hex[:10]
    output_root = JOBS_DIR / work_id
    output_root.mkdir(parents=True, exist_ok=True)

    try:
        site_dir = gen.build_site(cfg, output_root)
    except Exception as e:
        shutil.rmtree(output_root, ignore_errors=True)
        return jsonify({"error": f"Generation failed: {e}"}), 500

    # ---- overlay any uploaded images onto the placeholders ----
    images_dir = site_dir / "assets" / "images"
    manifest_path = images_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    size_by_filename = {m["filename"]: (m["width"], m["height"]) for m in manifest}

    # These are shown full-bleed at large sizes (hero banner, "what is"
    # product shot) -- cropping them looks broken, so preserve the whole
    # photo. Everything else (ingredient tiles, pricing tiers, avatars)
    # keeps the existing cover-crop for uniform grid framing.
    NO_CROP_SUFFIXES = {
        "hero", "product-main", "pricing", "certified",
        "free-shipping", "checkout-page", "og-image", "twitter-image",
    }

    # Uploaded photos are used exactly as provided -- no background
    # removal, no color changes, no other processing of any kind. The
    # ONLY thing ever applied is the resize/crop needed to fit the
    # section's layout box, which is unavoidable for consistent page
    # layout. Nothing touches the photo's actual pixel content or colors.
    for field_name in request.files:
        if not field_name.startswith("image_"):
            continue
        file_storage = next(
            (
                candidate
                for candidate in reversed(request.files.getlist(field_name))
                if candidate and candidate.filename
            ),
            None,
        )
        if not file_storage:
            continue
        suffix = field_name[len("image_"):]
        target_filename = f"{cfg['_slug']}-{suffix}.webp"
        target_path = images_dir / target_filename
        w, h = size_by_filename.get(target_filename, (1200, 900))
        crop_mode = "contain" if suffix in NO_CROP_SUFFIXES else "cover"
        try:
            images_mod.save_uploaded_image(file_storage.stream, target_path, w, h,
                                            crop_mode=crop_mode)
        except Exception as e:
            print(f"[api_generate] Skipped upload for {field_name}: {e}")

    # ---- zip the result ----
    zip_base = JOBS_DIR / work_id  # shutil appends .zip
    # Archive the generated site's contents so index.html is at the ZIP root.
    zip_path = shutil.make_archive(str(zip_base), "zip", site_dir)

    download_name = f"{cfg['_slug']}-website.zip"
    resp = send_file(zip_path, as_attachment=True, download_name=download_name,
                      mimetype="application/zip")

    @resp.call_on_close
    def _cleanup():
        shutil.rmtree(output_root, ignore_errors=True)
        Path(zip_path).unlink(missing_ok=True)

    return resp


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Uploaded file too large (max 8MB per image)."}), 413


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the landing page generator web app.")
    parser.add_argument("--port", type=int, default=5000, help="Port to run on (default: 5000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    args = parser.parse_args()

    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024 * 15  # up to ~15 image fields x 8MB

    print(f"\nLanding Page Generator running at http://{args.host}:{args.port}\n")

    try:
        # use_reloader=False: this tool doesn't need live-reload (you're not
        # editing app.py while it runs), and the auto-reloader's restart-on-
        # startup behavior is what caused a false "port already in use" on
        # Windows in an earlier version of this script.
        app.run(debug=True, use_reloader=False, host=args.host, port=args.port)
    except OSError as e:
        print(f"\n❌ Could not bind to {args.host}:{args.port} ({e}).")
        print("This usually means the port is already in use or blocked/reserved by Windows.")
        print("Try a different port, for example:\n")
        print(f"    python app.py --port {args.port + 1}\n")
        raise SystemExit(1)
