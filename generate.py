#!/usr/bin/env python3
"""
generate.py
-----------
Landing page website generator (Python).

Usage:
    python3 generate.py --config config.example.json
    python3 generate.py --config my_product.json --output Products

This reads a JSON config describing your product (see config.example.json),
then builds:

    Products/<Category>/
        index.html
        privacy-policy.html
        disclaimer.html
        affiliate-disclosure.html
        medical-disclaimer.html
        terms-and-conditions.html
        shipping-policy.html
        refund-policy.html
        contact.html
        404.html
        sitemap.xml
        robots.txt
        assets/
            css/style.css, responsive.css
            js/script.js
            images/*.webp  (placeholders + manifest.json)
"""

import argparse
import json
import re
import shutil
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import env_loader
env_loader.load_env_file()

import site_content
import seo as seo_mod
import images as images_mod
import ai_content
import references as references_mod

DEFAULT_CTA_LABEL = {
    "supplement": "Buy Now",
    "education": "Enroll Now",
    "business": "Get a Quote",
    "product": "Start Free Trial",
    "betting": "Claim Your Bonus",
}

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

CUSTOM_TEMPLATES = {
    "cardio-slim-tea": {
        "label": "Cardio Slim Tea Style",
        "description": "Use the uploaded multi-page supplement layout as the design template.",
        "site_types": ["supplement"],
        "brand_colors": {
            "primary": "#133D8C",
            "secondary": "#F16A7B",
            "dark": "#FCCF02",
            "light": "#ECECEC",
        },
        "dir": TEMPLATES_DIR / "custom" / "cardio-slim-tea",
    },
    "sodaslim-health": {
        "label": "SodaSlim Health Style",
        "description": "Use the SodaSlim supplement layout with navy, gold, trust cards, reviews, and pricing blocks.",
        "site_types": ["supplement"],
        "brand_colors": {
            "primary": "#132A3A",
            "secondary": "#F2AE30",
            "dark": "#0C1D29",
            "light": "#FBF8F1",
        },
        "dir": TEMPLATES_DIR / "custom" / "sodaslim-health",
    },
    "mind-wake": {
        "label": "Mind Wake Style",
        "description": "Use the Mind Wake cognitive wellness layout with green, gold, product showcases, reviews, and ingredient blocks.",
        "site_types": ["supplement"],
        "brand_colors": {
            "primary": "#1D291D",
            "secondary": "#F4B63F",
            "dark": "#1E1B17",
            "light": "#F7FAF6",
        },
        "dir": TEMPLATES_DIR / "custom" / "mind-wake",
    },
}

CUSTOM_IMAGE_SPECS = [
    ("favicon", "favicon.ico", 512, 512, "Logo favicon"),
    ("og-image", "index-meta.webp", 1200, 630, "Social share image"),
    ("twitter-image", "index-meta.webp", 1200, 600, "Twitter/X share image"),
    ("hero", "cardio-slim-tea-3-pouch.webp", 400, 320, "Hero product image"),
    ("product-main", "cardio-slim-tea-2-pouch.webp", 520, 375, "Main product image"),
    ("product-package-1", "cardio-slim-tea-2-pouch.webp", 520, 375, "Two pouch package"),
    ("product-package-2", "cardio-slim-tea-3-pouch.webp", 400, 320, "Three pouch package"),
    ("product-package-3", "cardio-slim-tea-6-pouch.webp", 520, 320, "Six pouch package"),
    ("pricing", "cardio-slim-tea-price.webp", 1037, 916, "Pricing package image"),
    ("customer-review-1", "cardio-slim-tea-customer-reviews-1.webp", 125, 145, "Customer review photo"),
    ("customer-review-2", "cardio-slim-tea-customer-reviews-2.webp", 125, 125, "Customer review photo"),
    ("customer-review-3", "cardio-slim-tea-customer-reviews-3.webp", 125, 125, "Customer review photo"),
    ("guarantee", "cardio-slim-tea-money-back-gurantee.webp", 474, 313, "Money-back guarantee badge"),
    ("certified", "certifications.webp", 1761, 297, "Certification badges"),
    ("free-shipping", "cardio-slim-tea-free-shipping.webp", 592, 591, "Free shipping image"),
    ("checkout-page", "cardio-slim-tea-checkout-page.webp", 909, 1759, "Checkout page preview"),
    ("bonus-1", "cardio-slim-tea-bonus-1.webp", 509, 291, "Bonus image"),
    ("bonus-2", "cardio-slim-tea-bonus-2.webp", 400, 514, "Bonus image"),
    ("bonus-3", "cardio-slim-tea-bonus-3.webp", 509, 500, "Bonus image"),
]

SODASLIM_IMAGE_SPECS = [
    ("favicon", "favicon.webp", 512, 512, "Logo favicon"),
    ("og-image", "og-image.jpg", 1200, 630, "Social share image"),
    ("twitter-image", "og-image.jpg", 1200, 600, "Twitter/X share image"),
    ("hero", "sodaslim-banner.webp", 700, 560, "Hero product image"),
    ("product-main", "sodaslim-3.webp", 700, 520, "Main product image"),
    ("product-package-1", "sodaslim-1.webp", 520, 380, "Basic package"),
    ("product-package-2", "sodaslim-3.webp", 520, 380, "Three bottle package"),
    ("product-package-3", "sodaslim-6.webp", 520, 380, "Six bottle package"),
    ("customer-review-1", "sodaslim-rev1.webp", 240, 240, "Customer review photo"),
    ("customer-review-2", "sodaslim-rev2.webp", 240, 240, "Customer review photo"),
    ("customer-review-3", "sodaslim-rev3.webp", 240, 240, "Customer review photo"),
    ("guarantee", "sodaslim-moneyback.webp", 520, 360, "Money-back guarantee badge"),
    ("certified", "sodaslim-gmp.webp", 520, 360, "Certification badge"),
    ("free-shipping", "sodaslim-level.webp", 592, 591, "Support image"),
    ("checkout-page", "sodaslim-checkout.webp", 909, 1759, "Checkout page preview"),
    ("ingredient-1", "sodaslim-ing1.webp", 480, 320, "Ingredient image"),
    ("ingredient-2", "sodaslim-ing2.webp", 480, 320, "Ingredient image"),
    ("ingredient-3", "sodaslim-ing3.webp", 480, 320, "Ingredient image"),
    ("ingredient-4", "sodaslim-ing4.webp", 480, 320, "Ingredient image"),
    ("ingredient-5", "sodaslim-ing5.webp", 480, 320, "Ingredient image"),
    ("bonus-1", "sodaslim-bonus-1.webp", 509, 500, "Bonus image"),
    ("bonus-2", "sodaslim-bonus-2.webp", 509, 500, "Bonus image"),
    ("bonus-3", "sodaslim-bonus-3.webp", 509, 500, "Bonus image"),
]

MINDWAKE_IMAGE_SPECS = [
    ("favicon", "favicon.webp", 512, 512, "Logo favicon"),
    ("og-image", "og-image.jpg", 1200, 630, "Social share image"),
    ("twitter-image", "og-image.jpg", 1200, 600, "Twitter/X share image"),
    ("hero", "Hero.webp", 700, 560, "Hero product image"),
    ("product-main", "mindwake6.webp", 700, 520, "Main product image"),
    ("product-package-1", "mindwake-1.webp", 520, 380, "Basic package"),
    ("product-package-2", "mindwake-2.webp", 520, 380, "Two bottle package"),
    ("product-package-3", "mindwake-3.webp", 520, 380, "Three bottle package"),
    ("customer-review-1", "mindwake-reviwes1.webp", 240, 240, "Customer review photo"),
    ("customer-review-2", "mindwake-reviwes2.webp", 240, 240, "Customer review photo"),
    ("customer-review-3", "mindwake-reviwes3.webp", 240, 240, "Customer review photo"),
    ("guarantee", "mindwake-guarantee.webp", 520, 360, "Money-back guarantee badge"),
    ("certified", "mindwake-gmp.webp", 520, 360, "Certification badge"),
    ("free-shipping", "mindwake-natural.webp", 592, 591, "Natural support image"),
    ("checkout-page", "mindwake-orderpage.webp", 909, 1759, "Checkout page preview"),
    ("ingredient-1", "mindwake-ing1.webp", 480, 320, "Ingredient image"),
    ("ingredient-2", "mindwake-ing2.webp", 480, 320, "Ingredient image"),
    ("ingredient-3", "mindwake-ing3.webp", 480, 320, "Ingredient image"),
    ("ingredient-4", "mindwake-ing4.webp", 480, 320, "Ingredient image"),
    ("ingredient-5", "mindwake-ing5.webp", 480, 320, "Ingredient image"),
    ("ingredient-6", "mindwake-ing6.webp", 480, 320, "Ingredient image"),
]

CUSTOM_TEMPLATE_IMAGE_SPECS = {
    "cardio-slim-tea": CUSTOM_IMAGE_SPECS,
    "sodaslim-health": SODASLIM_IMAGE_SPECS,
    "mind-wake": MINDWAKE_IMAGE_SPECS,
}

def _image_slot_catalog(template_id):
    return [
        {"suffix": suffix, "label": alt, "width": width, "height": height}
        for suffix, _source_name, width, height, alt in CUSTOM_TEMPLATE_IMAGE_SPECS.get(template_id, CUSTOM_IMAGE_SPECS)
    ]


def get_template_catalog():
    templates = [{
        "id": "default",
        "label": "Default Generator",
        "description": "Use the current flexible section-based design.",
        "site_types": site_content.SITE_TYPES,
        "default": True,
    }]
    for template_id, meta in CUSTOM_TEMPLATES.items():
        templates.append({
            "id": template_id,
            "label": meta["label"],
            "description": meta["description"],
            "site_types": meta["site_types"],
            "brand_colors": meta.get("brand_colors"),
            "image_slots": _image_slot_catalog(template_id),
            "default": False,
        })
    return templates


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def _legal_privacy_policy(cfg):
    biz = cfg["business_name"]
    email = cfg["contact_email"]
    domain = cfg["domain"].rstrip("/")
    return (
        f"<p>{biz} ("+"\"we,\" \"us,\" or \"our\") respects your privacy and is "
        f"committed to protecting the personal information you share with us. "
        f"This Privacy Policy explains what information we collect, why we "
        f"collect it, how we use and protect it, and the choices and rights "
        f"you have regarding your own data.</p>"
        f"<p>This policy applies to {domain} and any related services, "
        f"forms, or checkout pages operated by {biz}. By using this site, "
        f"you agree to the practices described here. If you do not agree, "
        f"please do not use the site.</p>"
        f"<h2>Information We Collect</h2>"
        f"<p>We collect information you provide directly to us, such as your "
        f"name, email address, shipping address, and payment details when "
        f"you place an order, contact support, or sign up for updates.</p>"
        f"<p>We also automatically collect certain technical information "
        f"when you visit our site, including your IP address, browser type, "
        f"device information, pages viewed, and the date and time of your "
        f"visit, typically gathered through cookies and similar technologies.</p>"
        f"<h2>How We Use Your Information</h2>"
        f"<p>We use the information we collect to process and fulfill "
        f"orders, respond to your questions, send order and shipping "
        f"confirmations, and provide customer support.</p>"
        f"<p>We may also use your information, with your consent where "
        f"required, to send marketing communications, improve our website "
        f"and offerings, detect and prevent fraud, and comply with legal "
        f"obligations.</p>"
        f"<h2>Cookies and Tracking Technologies</h2>"
        f"<p>Like most websites, we use cookies and similar tracking "
        f"technologies to remember your preferences, understand how "
        f"visitors use our site, and support analytics and advertising. You "
        f"can control cookies through your browser settings, though "
        f"disabling them may affect site functionality.</p>"
        f"<h2>How We Share Information</h2>"
        f"<p>We do not sell your personal information. We may share it "
        f"with trusted third-party service providers who help us operate "
        f"our business - such as payment processors, shipping carriers, "
        f"email providers, and analytics services - solely to perform "
        f"services on our behalf.</p>"
        f"<p>We may also disclose information if required by law, to "
        f"protect our rights, or in connection with a business transfer "
        f"such as a merger or acquisition.</p>"
        f"<h2>Data Security</h2>"
        f"<p>We use reasonable administrative, technical, and physical "
        f"safeguards designed to protect your information from unauthorized "
        f"access, loss, or misuse. However, no method of transmission or "
        f"storage is 100% secure, and we cannot guarantee absolute "
        f"security.</p>"
        f"<h2>Your Rights and Choices</h2>"
        f"<p>Depending on where you live, you may have the right to "
        f"request access to, correction of, or deletion of your personal "
        f"data, and to opt out of marketing communications at any time by "
        f"using the unsubscribe link in our emails or contacting us "
        f"directly.</p>"
        f"<h2>Children's Privacy</h2>"
        f"<p>Our site is not directed at children under 13 (or the "
        f"relevant minimum age in your jurisdiction), and we do not "
        f"knowingly collect personal information from children.</p>"
        f"<h2>Changes to This Policy</h2>"
        f"<p>We may update this Privacy Policy from time to time. Changes "
        f"will be posted on this page with an updated revision date, and "
        f"your continued use of the site after changes take effect "
        f"constitutes acceptance of the updated policy.</p>"
        f"<h2>Contact Us</h2>"
        f"<p>If you have questions about this Privacy Policy or how we "
        f"handle your data, please contact us at {email}.</p>"
    )


def _legal_disclaimer(cfg):
    biz = cfg["business_name"]
    email = cfg["contact_email"]
    return (
        f"<p>The information provided on this website by {biz} is for "
        f"general informational and educational purposes only. It does not "
        f"constitute professional advice of any kind, and nothing on this "
        f"site should be relied upon as a substitute for advice from a "
        f"qualified professional in the relevant field.</p>"
        f"<h2>No Warranties</h2>"
        f"<p>We make reasonable efforts to keep the information on this "
        f"site accurate and up to date, but we make no representations or "
        f"warranties of any kind, express or implied, about the "
        f"completeness, accuracy, reliability, suitability, or availability "
        f"of the site or the information it contains.</p>"
        f"<p>Any reliance you place on information from this site is "
        f"strictly at your own risk.</p>"
        f"<h2>Accuracy of Content</h2>"
        f"<p>While we strive to present information that is current and "
        f"correct at the time of publication, website content can become "
        f"outdated as products, offers, or circumstances change, and we are "
        f"under no obligation to update every page immediately.</p>"
        f"<h2>Individual Results May Vary</h2>"
        f"<p>Any results, outcomes, testimonials, or examples referenced on "
        f"this site are illustrative and individual results will vary based "
        f"on personal circumstances. Past results do not guarantee future "
        f"outcomes.</p>"
        f"<h2>External Links</h2>"
        f"<p>This site may contain links to third-party websites or "
        f"services that are not owned or controlled by {biz}. We have no "
        f"control over, and assume no responsibility for, the content, "
        f"privacy practices, or policies of any third-party sites.</p>"
        f"<h2>Limitation of Liability</h2>"
        f"<p>In no event will {biz} be liable for any loss or damage "
        f"arising from your use of this site, including but not limited to "
        f"indirect, incidental, or consequential damages.</p>"
        f"<h2>Professional Advice</h2>"
        f"<p>Nothing on this site should be construed as medical, legal, "
        f"financial, or other professional advice. Always seek the advice "
        f"of a qualified professional with any questions specific to your "
        f"situation.</p>"
        f"<p>You should never disregard professional advice or delay "
        f"seeking it because of something you read on this site.</p>"
        f"<h2>Changes to This Disclaimer</h2>"
        f"<p>We may revise this disclaimer at any time by updating this "
        f"page. You are encouraged to review it periodically for changes.</p>"
        f"<h2>Contact Us</h2>"
        f"<p>Questions about this disclaimer can be directed to {email}.</p>"
    )


def _legal_affiliate_disclosure(cfg):
    biz = cfg["business_name"]
    email = cfg["contact_email"]
    return (
        f"<p>{biz} is committed to transparency with our audience. This "
        f"page discloses our use of affiliate relationships in accordance "
        f"with the Federal Trade Commission's (FTC) guidelines on "
        f"endorsements and affiliate marketing.</p>"
        f"<h2>What Are Affiliate Links?</h2>"
        f"<p>Some of the links on this website are affiliate links. This "
        f"means that if you click on a link and make a purchase, we may "
        f"receive a commission from the retailer or service provider, at "
        f"no additional cost to you.</p>"
        f"<p>Affiliate links may appear as text links, images, banners, or "
        f"buttons anywhere on this site, including within product "
        f"descriptions, comparison tables, and blog-style content.</p>"
        f"<h2>Why We Use Affiliate Links</h2>"
        f"<p>Affiliate commissions help support the operation of this "
        f"website, including hosting costs, content creation, and ongoing "
        f"maintenance, so that we can continue offering free information "
        f"and resources to our visitors.</p>"
        f"<p>Without this revenue model, we would need to rely on other "
        f"forms of monetization, such as paid subscriptions or intrusive "
        f"advertising, which we've chosen not to pursue.</p>"
        f"<h2>Our Editorial Independence</h2>"
        f"<p>Our opinions and recommendations are our own. We only "
        f"recommend products or services we believe provide genuine value "
        f"to our readers, and affiliate relationships do not influence the "
        f"honesty of our content.</p>"
        f"<p>We are not compensated for writing positive reviews, and "
        f"commissions do not change the price you pay.</p>"
        f"<h2>Third-Party Products</h2>"
        f"<p>Any products or services linked from this site are subject to "
        f"the terms, conditions, and policies of the third-party seller. We "
        f"are not responsible for the accuracy of claims made by third "
        f"parties or for the fulfillment of orders placed through affiliate "
        f"links.</p>"
        f"<h2>Your Trust Matters</h2>"
        f"<p>We take our responsibility to our readers seriously, and this "
        f"disclosure exists so you always know when a link may result in "
        f"compensation to us.</p>"
        f"<h2>Contact Us</h2>"
        f"<p>If you have questions about our affiliate relationships, "
        f"contact us at {email}.</p>"
    )


def _legal_medical_disclaimer(cfg):
    biz = cfg["business_name"]
    email = cfg["contact_email"]
    return (
        f"<p>The content on this website, including text, graphics, "
        f"images, and other material published by {biz}, is provided for "
        f"general informational and educational purposes only. It is not "
        f"intended to be, and should not be taken as, a substitute for "
        f"professional medical advice, diagnosis, or treatment.</p>"
        f"<h2>Not a Substitute for Medical Advice</h2>"
        f"<p>Always seek the advice of your physician or other qualified "
        f"health provider with any questions you may have regarding a "
        f"medical condition, and before starting any new supplement, diet, "
        f"or exercise program.</p>"
        f"<p>Never disregard professional medical advice or delay seeking "
        f"it because of something you have read on this website.</p>"
        f"<h2>Special Populations</h2>"
        f"<p>If you are pregnant, nursing, taking medication, under 18, or "
        f"managing a health condition, consult your doctor before using any "
        f"product referenced on this site.</p>"
        f"<h2>Possible Interactions and Allergens</h2>"
        f"<p>Supplements can interact with medications or existing health "
        f"conditions, and individual sensitivities or allergies to "
        f"ingredients are possible. Always review the full ingredient list "
        f"on the product label and consult a healthcare provider if you "
        f"have any known allergies or are taking prescription medication.</p>"
        f"<h2>FDA Statement</h2>"
        f"<p>Statements regarding dietary supplements on this website have "
        f"not been evaluated by the Food and Drug Administration (FDA). "
        f"Products discussed on this site are not intended to diagnose, "
        f"treat, cure, or prevent any disease.</p>"
        f"<h2>Individual Results May Vary</h2>"
        f"<p>Testimonials and examples on this site reflect individual "
        f"experiences and are not a guarantee of the results you will "
        f"achieve. Results vary based on individual biology, consistency of "
        f"use, and other factors outside our control.</p>"
        f"<h2>Emergency Situations</h2>"
        f"<p>If you believe you may be experiencing a medical emergency, "
        f"call your local emergency number or go to the nearest emergency "
        f"room immediately. Do not rely on this website for emergency "
        f"medical guidance.</p>"
        f"<h2>No Doctor-Patient Relationship</h2>"
        f"<p>Use of this website does not create a doctor-patient "
        f"relationship between you and {biz} or any of its contributors.</p>"
        f"<h2>Contact Us</h2>"
        f"<p>Questions about this medical disclaimer can be sent to "
        f"{email}.</p>"
    )


def _legal_terms(cfg):
    biz = cfg["business_name"]
    email = cfg["contact_email"]
    domain = cfg["domain"].rstrip("/")
    return (
        f"<p>These Terms &amp; Conditions ("+"\"Terms\") govern your access "
        f"to and use of {domain}, operated by {biz}. By accessing or using "
        f"this site, you agree to be bound by these Terms. If you do not "
        f"agree, please do not use the site.</p>"
        f"<h2>Use of the Site</h2>"
        f"<p>You agree to use this site only for lawful purposes and in a "
        f"way that does not infringe the rights of, or restrict or inhibit "
        f"the use and enjoyment of, this site by any third party.</p>"
        f"<p>You agree not to attempt to gain unauthorized access to any "
        f"part of the site, interfere with its operation, or use automated "
        f"means to scrape or collect data from the site without permission.</p>"
        f"<h2>Intellectual Property</h2>"
        f"<p>All content on this site, including text, graphics, logos, "
        f"and images, is the property of {biz} or its licensors and is "
        f"protected by applicable intellectual property laws. You may not "
        f"reproduce, distribute, or create derivative works without our "
        f"written permission.</p>"
        f"<h2>Orders and Payment</h2>"
        f"<p>By placing an order through this site, you represent that you "
        f"are authorized to use the payment method provided and that the "
        f"information you supply is accurate and complete.</p>"
        f"<p>We reserve the right to refuse or cancel any order at our "
        f"discretion, including in cases of suspected fraud or pricing "
        f"errors.</p>"
        f"<h2>Disclaimer of Warranties</h2>"
        f"<p>This site and all content are provided "+"\"as is\" and "
        f"\"as available\" without warranties of any kind, either express "
        f"or implied, including but not limited to warranties of "
        f"merchantability or fitness for a particular purpose.</p>"
        f"<h2>Limitation of Liability</h2>"
        f"<p>To the fullest extent permitted by law, {biz} shall not be "
        f"liable for any indirect, incidental, special, or consequential "
        f"damages arising out of or related to your use of this site.</p>"
        f"<h2>Changes to These Terms</h2>"
        f"<p>We reserve the right to modify these Terms at any time. "
        f"Changes take effect immediately upon posting, and your continued "
        f"use of the site constitutes acceptance of the revised Terms.</p>"
        f"<h2>Governing Law</h2>"
        f"<p>These Terms are governed by applicable law in the jurisdiction "
        f"where {biz} operates, without regard to its conflict of law "
        f"provisions.</p>"
        f"<h2>Contact Us</h2>"
        f"<p>Questions about these Terms can be directed to {email}.</p>"
    )


def _legal_shipping_policy(cfg):
    biz = cfg["business_name"]
    email = cfg["contact_email"]
    return (
        f"<p>This Shipping Policy explains how {biz} processes, ships, and "
        f"delivers orders, so you know what to expect after you check "
        f"out.</p>"
        f"<h2>Order Processing</h2>"
        f"<p>Orders are typically processed within 1-2 business days of "
        f"purchase. Orders placed on weekends or holidays are processed "
        f"the next business day.</p>"
        f"<h2>Delivery Times</h2>"
        f"<p>Domestic delivery generally takes 3-10 business days "
        f"depending on your location and the shipping method selected at "
        f"checkout. International delivery times vary by destination and "
        f"customs processing, and can take longer.</p>"
        f"<p>These are estimates, not guarantees - delays can occur due to "
        f"weather, carrier issues, or high order volume that are outside "
        f"our control.</p>"
        f"<h2>Order Tracking</h2>"
        f"<p>Once your order ships, you'll receive a confirmation email "
        f"with a tracking number so you can follow your package's progress "
        f"to your door.</p>"
        f"<h2>Shipping Costs</h2>"
        f"<p>Shipping costs, if any, are calculated and displayed at "
        f"checkout before you complete your purchase. Any promotional free "
        f"shipping offers will be clearly noted on the order page.</p>"
        f"<h2>Incorrect Addresses</h2>"
        f"<p>Please double-check your shipping address before completing "
        f"your order. We are not responsible for packages delayed or lost "
        f"due to an incorrect address provided at checkout.</p>"
        f"<h2>Lost or Damaged Packages</h2>"
        f"<p>If your package arrives damaged or does not arrive within the "
        f"expected timeframe, contact us and we'll work with the carrier "
        f"to resolve the issue as quickly as possible.</p>"
        f"<h2>International Orders</h2>"
        f"<p>International customers are responsible for any customs "
        f"duties, taxes, or import fees charged by their country, which "
        f"are not included in the order total.</p>"
        f"<h2>Contact Us</h2>"
        f"<p>Questions about shipping can be directed to {email}.</p>"
    )


def _legal_refund_policy(cfg):
    biz = cfg["business_name"]
    email = cfg["contact_email"]
    return (
        f"<p>{biz} wants you to be genuinely satisfied with your purchase. "
        f"This Refund Policy explains how refunds and returns work.</p>"
        f"<h2>Guarantee Window</h2>"
        f"<p>If you are not fully satisfied with your purchase, contact "
        f"our support team within the guarantee window stated on the "
        f"product or pricing page for return and refund instructions.</p>"
        f"<h2>How to Request a Refund</h2>"
        f"<p>To request a refund, email our support team with your order "
        f"number and the reason for your request. We aim to respond to all "
        f"refund requests within 1-2 business days.</p>"
        f"<h2>Processing Refunds</h2>"
        f"<p>Approved refunds are processed to the original payment method "
        f"used at checkout. Depending on your bank or card issuer, it may "
        f"take 5-10 business days for the refund to appear on your "
        f"statement.</p>"
        f"<h2>Return Shipping</h2>"
        f"<p>If a physical return is required as part of your refund, we "
        f"will provide instructions for returning the item. Depending on "
        f"the circumstances, return shipping costs may be the "
        f"responsibility of the customer.</p>"
        f"<h2>Non-Refundable Items</h2>"
        f"<p>Certain items, such as opened or used products outside the "
        f"guarantee window, or promotional/bonus items, may not be "
        f"eligible for a refund. Any such exceptions will be noted on the "
        f"product page.</p>"
        f"<h2>Partial Refunds</h2>"
        f"<p>In some cases, we may offer a partial refund depending on the "
        f"condition of a returned item or the circumstances of the "
        f"request, at our discretion.</p>"
        f"<h2>Order Cancellations</h2>"
        f"<p>If you need to cancel an order, contact us as soon as "
        f"possible. If the order has not yet shipped, we will do our best "
        f"to cancel it before it processes.</p>"
        f"<h2>Disputed Charges</h2>"
        f"<p>If you believe a charge was made in error, please contact us "
        f"directly before filing a dispute with your bank or card issuer - "
        f"most billing questions can be resolved faster this way, and it "
        f"helps us keep serving customers without unnecessary chargebacks.</p>"
        f"<h2>Contact Us</h2>"
        f"<p>For any refund-related questions, reach out to {email} - "
        f"we'd rather resolve it directly than leave you unsatisfied.</p>"
    )


def _legal_responsible_gambling(cfg):
    biz = cfg["business_name"]
    email = cfg["contact_email"]
    return (
        f"<p>{biz} is committed to promoting responsible play. This page "
        f"outlines the tools available to you and where to find help if "
        f"gambling stops being fun.</p>"
        f"<h2>Age Requirement</h2>"
        f"<p>You must meet the minimum legal gambling age in your "
        f"jurisdiction to create an account or use this platform. Age "
        f"verification may be required before you can withdraw funds.</p>"
        f"<h2>Gambling Should Be Entertainment</h2>"
        f"<p>Gambling should be treated as entertainment, not a way to "
        f"make money or escape financial or personal problems. Only wager "
        f"what you can genuinely afford to lose, and never borrow money to "
        f"gamble.</p>"
        f"<p>Never chase losses by increasing your bets to try to win back "
        f"money you've already lost - this is one of the clearest warning "
        f"signs of a developing problem.</p>"
        f"<h2>Tools Available to You</h2>"
        f"<p>Deposit limits, wager limits, time-outs, and self-exclusion "
        f"options are available in your account settings at any time, "
        f"letting you set boundaries that work for you.</p>"
        f"<p>Once a self-exclusion period is set, it cannot be reversed "
        f"early just by asking - that delay is intentional, since it's "
        f"there to protect you during moments when you might otherwise "
        f"reverse the decision impulsively.</p>"
        f"<h2>Warning Signs</h2>"
        f"<p>Signs that gambling may be becoming a problem include betting "
        f"more than you can afford, lying about how much you gamble, "
        f"neglecting responsibilities, and feeling anxious or irritable "
        f"when not gambling.</p>"
        f"<h2>Getting Help</h2>"
        f"<p>If gambling is no longer fun or is causing problems for you "
        f"or someone you know, free and confidential help is available. In "
        f"the US, contact the National Council on Problem Gambling at "
        f"1-800-522-4700 or visit ncpgambling.org. Outside the US, search "
        f"for your national problem gambling helpline.</p>"
        f"<h2>Supporting a Loved One</h2>"
        f"<p>If you're concerned about someone else's gambling, "
        f"organizations like Gam-Anon offer support specifically for "
        f"family members and friends affected by someone else's gambling.</p>"
        f"<h2>Contact Us</h2>"
        f"<p>For questions about our responsible gambling tools, contact "
        f"us at {email}.</p>"
    )


LEGAL_PAGES = {
    "privacy-policy.html": ("Privacy Policy", _legal_privacy_policy),
    "disclaimer.html": ("General Disclaimer", _legal_disclaimer),
    "affiliate-disclosure.html": ("Affiliate Disclosure", _legal_affiliate_disclosure),
    "medical-disclaimer.html": ("Medical Disclaimer", _legal_medical_disclaimer),
    "terms-and-conditions.html": ("Terms & Conditions", _legal_terms),
    "shipping-policy.html": ("Shipping Policy", _legal_shipping_policy),
    "refund-policy.html": ("Refund Policy", _legal_refund_policy),
    "responsible-gambling.html": ("Responsible Gambling", _legal_responsible_gambling),
}


def validate_and_fill_config(cfg):
    """Validates required fields and fills in defaults on an in-memory
    config dict. Used by the CLI (from a loaded JSON file), the
    interactive wizard, and the web app (from form data)."""
    required = ["product_name", "category", "official_website",
                "primary_keyword", "domain"]
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        raise ValueError(f"Missing required config fields: {missing}")

    cfg.setdefault("secondary_keywords", [])
    cfg.setdefault("brand_colors", {"primary": "#1F6F54", "secondary": "#F4A63E",
                                     "dark": "#123328", "light": "#FBF7EE"})
    cfg.setdefault("business_name", cfg["product_name"])
    cfg.setdefault("contact_email", "support@example.com")
    cfg.setdefault("affiliate_link", cfg["official_website"])
    cfg.setdefault("price", {"one_bottle": "69", "three_bottle_each": "59",
                              "six_bottle_each": "49", "currency": "USD"})
    cfg.setdefault("tier_labels", [])  # e.g. ["2 Bottles", "3 Bottles", "6 Bottles"] to override defaults
    cfg.setdefault("rating", {"value": "4.8", "count": "100"})
    cfg.setdefault("use_ai_content", False)
    cfg.setdefault("fail_on_ai_error", False)
    cfg.setdefault("ai_provider", "anthropic")
    cfg.setdefault("site_type", "product")
    if cfg["site_type"] not in site_content.SITE_TYPES:
        raise ValueError(
            f"site_type must be one of {site_content.SITE_TYPES}, got {cfg['site_type']!r}"
        )
    cfg.setdefault("cta_label", DEFAULT_CTA_LABEL.get(cfg["site_type"], "Get Started"))
    cfg.setdefault("cta_href", cfg["affiliate_link"])
    cfg.setdefault("selected_sections", None)  # None = use type defaults
    cfg.setdefault("randomize_section_order", True)
    cfg.setdefault("reference_sites", [])
    cfg.setdefault("anthropic_api_key", None)  # entered per-request in the wizard, never saved
    cfg.setdefault("openai_api_key", None)  # entered per-request in the wizard, never saved
    cfg.setdefault("ingredients_data", [])  # [{"name","description"}] - real ingredient copy
    cfg.setdefault("testimonials_data", [])  # [{"quote","name","role"}] - real testimonials
    cfg.setdefault("theme_overrides", {})  # optional custom-template copy overrides from the web editor
    cfg.setdefault("template_id", "default")
    if cfg["template_id"] not in ("default", *CUSTOM_TEMPLATES.keys()):
        raise ValueError(f"template_id must be one of {[t['id'] for t in get_template_catalog()]}")
    if cfg["template_id"] != "default":
        allowed_types = CUSTOM_TEMPLATES[cfg["template_id"]]["site_types"]
        if cfg["site_type"] not in allowed_types:
            raise ValueError(
                f"template_id {cfg['template_id']!r} is only available for {allowed_types}"
            )

    cfg["_slug"] = slugify(cfg["product_name"])
    return cfg


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return validate_and_fill_config(cfg)


def _currency_symbol(currency):
    return {"USD": "$", "EUR": "EUR ", "GBP": "GBP ", "INR": "INR "}.get(
        str(currency).upper(), f"{currency} "
    )


def _custom_image_manifest(cfg, template_dir, images_dir, template_id="cardio-slim-tea"):
    manifest = []
    source_dir = template_dir / "assets" / "images"
    no_crop = {"hero", "product-main", "og-image", "twitter-image", "certified", "free-shipping", "checkout-page"}

    for suffix, source_name, width, height, alt in CUSTOM_TEMPLATE_IMAGE_SPECS.get(template_id, CUSTOM_IMAGE_SPECS):
        filename = f"{cfg['_slug']}-{suffix}.webp"
        source_path = source_dir / source_name
        target_path = images_dir / filename
        if source_path.exists():
            with source_path.open("rb") as f:
                images_mod.save_uploaded_image(
                    f, target_path, width, height,
                    crop_mode="contain" if suffix in no_crop else "cover",
                )
        manifest.append({
            "filename": filename,
            "size": f"{width}x{height}",
            "width": width,
            "height": height,
            "alt": f"{cfg['product_name']} {alt}",
            "title": f"{cfg['product_name']} {alt}",
            "prompt": f"Replacement image for {cfg['product_name']} {alt.lower()}",
        })

    return manifest


def _custom_section_context(sections):
    section_map = {s.get("id"): s for s in sections}

    def sec(section_id):
        data = dict(section_map.get(section_id, {}))
        data.setdefault("items", [])
        data.setdefault("pros", [])
        data.setdefault("cons", [])
        data.setdefault("body", "")
        data.setdefault("title", "")
        return data

    return {
        "hero": sec("hero"),
        "what_is": sec("what_is"),
        "how_it_works": sec("how_it_works"),
        "benefits": sec("benefits"),
        "ingredients": sec("ingredients"),
        "testimonials": sec("testimonials"),
        "guarantee": sec("guarantee"),
        "usage": sec("usage"),
        "pros_cons": sec("pros_cons"),
        "where_to_buy": sec("where_to_buy"),
        "post_purchase": sec("post_purchase"),
        "faq": sec("faq"),
        "conclusion": sec("conclusion"),
    }


def _custom_faq_items(cfg, custom_context):
    items = custom_context.get("faq", {}).get("items") or []
    if items:
        return items
    return [{"q": q, "a": a} for q, a in seo_mod.build_faqs(cfg)]


def _custom_chrome_context(cfg):
    overrides = cfg.get("theme_overrides", {}) or {}
    product = cfg["product_name"]
    return {
        "brand": overrides.get("header_brand") or product,
        "nav_1": overrides.get("header_nav_1") or f"About {product}",
        "nav_2": overrides.get("header_nav_2") or "Benefits",
        "nav_3": overrides.get("header_nav_3") or "Pricing",
        "nav_4": overrides.get("header_nav_4") or "FAQ",
        "cta": overrides.get("header_cta") or cfg["cta_label"],
        "footer_title": overrides.get("footer_title") or "Conclusion",
        "footer_copyright": overrides.get("footer_copyright") or (
            f"Copyright {date.today().year} | {product} | All rights reserved."
        ),
    }


def _html_paragraphs(text):
    parts = [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]
    if not parts:
        return ""
    return "".join(f"<p>{p}</p>" for p in parts)


def _apply_theme_overrides(sections, overrides):
    if not overrides:
        return sections

    section_map = {s.get("id"): s for s in sections}

    field_map = {
        "hero": ("hero_title", "hero_body"),
        "what_is": ("what_title", "what_body"),
        "how_it_works": ("how_title", "how_body"),
        "benefits": ("benefits_title", "benefits_body"),
        "ingredients": ("ingredients_title", "ingredients_body"),
        "usage": ("usage_title", "usage_body"),
        "where_to_buy": ("where_title", "where_body"),
        "guarantee": ("guarantee_title", "guarantee_body"),
        "post_purchase": ("post_purchase_title", "post_purchase_body"),
        "conclusion": ("conclusion_title", "conclusion_body"),
    }

    for section_id, (title_key, body_key) in field_map.items():
        sec = section_map.get(section_id)
        if not sec:
            continue
        if overrides.get(title_key):
            sec["title"] = overrides[title_key]
        if overrides.get(body_key):
            sec["body"] = _html_paragraphs(overrides[body_key])

    faq_items = overrides.get("faq_items")
    if faq_items and section_map.get("faq"):
        section_map["faq"]["items"] = [
            {"q": item.get("q") or f"Question {i}", "a": item.get("a") or ""}
            for i, item in enumerate(faq_items, 1)
        ]

    return sections


def _build_custom_template_site(cfg, output_root, template_id, common, meta, schema):
    template_dir = CUSTOM_TEMPLATES[template_id]["dir"]
    env = Environment(loader=FileSystemLoader(str(template_dir)),
                      trim_blocks=True, lstrip_blocks=True)

    category_dir = output_root / cfg["category"].replace(" ", "")
    images_dir = category_dir / "assets" / "images"
    css_dir = category_dir / "assets" / "css"
    js_dir = category_dir / "assets" / "js"
    for d in (images_dir, css_dir, js_dir):
        d.mkdir(parents=True, exist_ok=True)

    assets_src = template_dir / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, category_dir / "assets", dirs_exist_ok=True)

    sections = site_content.build_sections(cfg)
    if cfg.get("use_ai_content"):
        sections = ai_content.rewrite_sections_with_ai(cfg, sections)
    sections = _apply_theme_overrides(sections, cfg.get("theme_overrides", {}))

    custom_context = _custom_section_context(sections)
    custom_context["faq"]["items"] = _custom_faq_items(cfg, custom_context)

    page_context = {
        **common,
        "domain": cfg["domain"].rstrip("/"),
        "brand_colors": cfg["brand_colors"],
        "price": cfg["price"],
        "currency_symbol": _currency_symbol(cfg["price"].get("currency", "USD")),
        "meta": meta,
        "schema": schema,
        "sections": sections,
        "custom": custom_context,
        "chrome": _custom_chrome_context(cfg),
    }

    css_template = template_dir / "assets" / "css" / "mystyle.css.j2"
    if css_template.exists():
        rendered_css = env.get_template("assets/css/mystyle.css.j2").render(**page_context)
        (css_dir / "mystyle.css").write_text(rendered_css, encoding="utf-8")

    for template_path in template_dir.glob("*.html.j2"):
        output_name = template_path.name[:-3]
        html = env.get_template(template_path.name).render(**page_context)
        (category_dir / output_name).write_text(html, encoding="utf-8")

    for static_path in template_dir.iterdir():
        if static_path.is_file() and not static_path.name.endswith(".j2"):
            if static_path.name in {"robots.txt", "sitemap.xml", ".htaccess"}:
                continue
            shutil.copy(static_path, category_dir / static_path.name)

    skip_pages = {"medical-disclaimer.html", "responsible-gambling.html"}
    (category_dir / "sitemap.xml").write_text(seo_mod.build_sitemap(cfg, skip_pages), encoding="utf-8")
    (category_dir / "robots.txt").write_text(seo_mod.build_robots(cfg), encoding="utf-8")
    (category_dir / ".htaccess").write_text(seo_mod.build_htaccess(cfg), encoding="utf-8")
    (category_dir / "llms.txt").write_text(seo_mod.build_llms_txt(cfg, sections), encoding="utf-8")

    manifest = _custom_image_manifest(cfg, template_dir, images_dir, template_id)
    (images_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return category_dir


def build_site(cfg, output_root):
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)),
                       trim_blocks=True, lstrip_blocks=True)

    category_dir = output_root / cfg["category"].replace(" ", "")
    images_dir = category_dir / "assets" / "images"
    css_dir = category_dir / "assets" / "css"
    js_dir = category_dir / "assets" / "js"
    for d in (images_dir, css_dir, js_dir):
        d.mkdir(parents=True, exist_ok=True)

    slug = cfg["_slug"]
    meta = seo_mod.build_meta(cfg)
    schema = seo_mod.build_schema(cfg)
    faqs = seo_mod.build_faqs(cfg)
    sections = site_content.build_sections(cfg)
    if cfg.get("use_ai_content"):
        sections = ai_content.rewrite_sections_with_ai(cfg, sections)

    common = {
        "product_name": cfg["product_name"],
        "category": cfg["category"],
        "site_type": cfg["site_type"],
        "slug": slug,
        "affiliate_link": cfg["affiliate_link"],
        "cta_label": cfg["cta_label"],
        "cta_href": cfg["cta_href"],
        "business_name": cfg["business_name"],
        "contact_email": cfg["contact_email"],
        "meta": meta,
        "domain": cfg["domain"].rstrip("/"),
        "brand_colors": cfg["brand_colors"],
        "price": cfg["price"],
        "rating": cfg["rating"],
        "year": date.today().year,
        "today": date.today().isoformat(),
    }

    if cfg.get("template_id") != "default":
        return _build_custom_template_site(
            cfg, output_root, cfg["template_id"], common, meta, schema
        )

    # ---- index.html ----
    index_html = env.get_template("index.html.j2").render(
        **common,
        sections=sections,
        schema=schema,
        faqs=faqs,
    )
    (category_dir / "index.html").write_text(index_html, encoding="utf-8")

    # ---- legal pages (skip ones irrelevant to this site type) ----
    skip_pages = set()
    if cfg["site_type"] != "supplement":
        skip_pages.add("medical-disclaimer.html")
    if cfg["site_type"] not in ("supplement", "product", "betting"):
        skip_pages.add("affiliate-disclosure.html")
    if cfg["site_type"] != "betting":
        skip_pages.add("responsible-gambling.html")

    for filename, (title, body_fn) in LEGAL_PAGES.items():
        if filename in skip_pages:
            continue
        html = env.get_template("legal.html.j2").render(
            **common, page_title=title, page_slug=filename, body=body_fn(cfg),
        )
        (category_dir / filename).write_text(html, encoding="utf-8")

    # ---- contact + 404 ----
    (category_dir / "contact.html").write_text(
        env.get_template("contact.html.j2").render(**common), encoding="utf-8")
    (category_dir / "404.html").write_text(
        env.get_template("404.html.j2").render(**common), encoding="utf-8")

    # ---- sitemap + robots ----
    (category_dir / "sitemap.xml").write_text(seo_mod.build_sitemap(cfg, skip_pages), encoding="utf-8")
    (category_dir / "robots.txt").write_text(seo_mod.build_robots(cfg), encoding="utf-8")

    # ---- technical SEO extras ----
    (category_dir / ".htaccess").write_text(seo_mod.build_htaccess(cfg), encoding="utf-8")
    (category_dir / "llms.txt").write_text(seo_mod.build_llms_txt(cfg, sections), encoding="utf-8")

    # ---- optional reference-site research notes (Step 15) ----
    notes = references_mod.build_reference_notes(cfg, cfg.get("reference_sites", []))
    if notes:
        (category_dir / "competitive-notes.md").write_text(notes, encoding="utf-8")

    # ---- css (rendered as jinja to inject colors) + js (static copy) ----
    def _hex_to_rgb(hex_color):
        h = hex_color.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        except (ValueError, IndexError):
            r, g, b = 31, 111, 84  # fallback to the default green
        return f"{r}, {g}, {b}"

    colors_with_rgb = dict(cfg["brand_colors"])
    colors_with_rgb["primary_rgb"] = _hex_to_rgb(cfg["brand_colors"]["primary"])
    colors_with_rgb["secondary_rgb"] = _hex_to_rgb(cfg["brand_colors"]["secondary"])
    colors_with_rgb["dark_rgb"] = _hex_to_rgb(cfg["brand_colors"]["dark"])

    css_env = Environment(loader=FileSystemLoader(str(STATIC_DIR)))
    style_css = css_env.get_template("style.css").render(colors=colors_with_rgb)
    (css_dir / "style.css").write_text(style_css, encoding="utf-8")
    shutil.copy(STATIC_DIR / "responsive.css", css_dir / "responsive.css")
    shutil.copy(STATIC_DIR / "script.js", js_dir / "script.js")

    # ---- images: manifest + placeholder renders ----
    manifest = images_mod.collect_manifest(cfg, sections)
    images_mod.render_placeholders(manifest, images_dir, cfg["brand_colors"]["primary"])
    (images_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    return category_dir


def load_config_dict(raw_cfg):
    """Same validation/defaults as load_config(), but from an in-memory
    dict (used by the interactive wizard and the web app)."""
    return validate_and_fill_config(dict(raw_cfg))


def main():
    parser = argparse.ArgumentParser(description="Generate a premium landing page site.")
    parser.add_argument("--config", help="Path to config JSON")
    parser.add_argument("--output", default="Products", help="Output root folder")
    parser.add_argument("--interactive", action="store_true",
                         help="Answer prompts instead of providing a config file")
    args = parser.parse_args()

    if args.interactive:
        import wizard
        cfg = load_config_dict(wizard.run_wizard())
    elif args.config:
        cfg = load_config(args.config)
    else:
        parser.error("Provide --config <file.json> or use --interactive")

    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    site_dir = build_site(cfg, output_root)

    if args.interactive:
        saved_cfg_path = output_root / f"{cfg['_slug']}-config.json"
        secret_keys = {"anthropic_api_key", "openai_api_key"}
        save_cfg = {k: v for k, v in cfg.items()
                    if not k.startswith("_") and k not in secret_keys}
        saved_cfg_path.write_text(json.dumps(save_cfg, indent=2), encoding="utf-8")
        print(f"Ã°Å¸â€™Â¾ Saved config to: {saved_cfg_path.resolve()} "
              f"(reuse with --config {saved_cfg_path})\n")

    print(f"\nOK Site generated at: {site_dir.resolve()}\n")
    print("Files created:")
    for p in sorted(site_dir.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(output_root)}")


if __name__ == "__main__":
    main()
