"""
ai_content.py
-------------
Optional pass: rewrites the copy inside an already-built section list
using Anthropic or OpenAI, so wording is fully unique per generation.

Only touches text fields (title, body, eyebrow, bullets, item text/
quote/bio/name/role); never touches structural keys.
"""

import copy
import json
import os
import re

TEXT_KEYS = {"title", "body", "eyebrow"}
ITEM_TEXT_KEYS = {"text", "quote", "bio", "name", "role"}


def _extract_text_map(sections):
    texts = {}
    for si, sec in enumerate(sections):
        for key in TEXT_KEYS:
            if sec.get(key):
                texts[f"{si}.{key}"] = sec[key]
        for bi, bullet in enumerate(sec.get("bullets", []) or []):
            if bullet:
                texts[f"{si}.bullets.{bi}"] = bullet
        for ii, item in enumerate(sec.get("items", [])):
            for key in ITEM_TEXT_KEYS:
                if item.get(key):
                    texts[f"{si}.items.{ii}.{key}"] = item[key]
    return texts


def _apply_text_map(sections, new_texts):
    sections = copy.deepcopy(sections)
    for path, value in new_texts.items():
        parts = path.split(".")
        if len(parts) == 2:
            si, key = int(parts[0]), parts[1]
            sections[si][key] = value
        elif len(parts) == 3:
            si, kind, bi = int(parts[0]), parts[1], int(parts[2])
            if kind == "bullets":
                sections[si]["bullets"][bi] = value
        elif len(parts) == 4:
            si, _, ii, key = int(parts[0]), parts[1], int(parts[2]), parts[3]
            sections[si]["items"][ii][key] = value
    return sections


def _word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def _paragraph_count(text):
    html_paragraphs = len(re.findall(r"<p\b", text or "", flags=re.IGNORECASE))
    if html_paragraphs:
        return html_paragraphs
    return len([p for p in re.split(r"\n\s*\n", text or "") if p.strip()]) or 1


def _length_guide(texts):
    return {
        path: {
            "words": _word_count(value),
            "paragraphs": _paragraph_count(value) if path.endswith(".body") else None,
        }
        for path, value in texts.items()
    }


def _build_prompt(cfg, texts):
    length_guide = _length_guide(texts)
    return f"""You are a senior conversion copywriter writing a landing page
for "{cfg['product_name']}" ({cfg['category']}, site type: {cfg.get('site_type')}).
Primary keyword: "{cfg['primary_keyword']}".

Below is a JSON object mapping field paths to the current copy. Rewrite
EVERY value to be 100% original, conversational, human-sounding,
persuasive copy. Do not invent statistics, medical claims, or fake
facts. Keep any medical/legal disclaimer meaning intact if present.

IMPORTANT DESIGN-FIT RULE: the generated text must keep the same visual
length as the original template copy. Do not expand sections into much
longer copy. Do not shrink detailed sections into short copy.

Length rules:
- For every key, match the word count from LENGTH_GUIDE within about
  15 percent where natural. If a field has 40 words, return roughly
  34-46 words. If it has 8 words, keep it short.
- Keys ending in ".body": keep the same number of paragraphs shown in
  LENGTH_GUIDE. If the original has <p> tags, return <p> tags too.
- Keys ending in ".bullets.N": keep these short and similar length.
- Keys ending in ".title" or ".eyebrow": keep these short and similar length.
- Keys under ".items.N.text", ".quote", ".bio": keep similar length.
- Keys under ".items.N.name" or ".role": leave these exactly as given.

Return ONLY a JSON object with the exact same keys, new string values.
No markdown fences, no preamble.

LENGTH_GUIDE:
{json.dumps(length_guide, indent=2)}

INPUT:
{json.dumps(texts, indent=2)}
"""


def _rewrite_with_anthropic(cfg, prompt):
    try:
        import anthropic
    except ImportError:
        print("[ai_content] `anthropic` not installed. Run: pip install anthropic")
        return None

    api_key = cfg.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ai_content] No Anthropic API key provided.")
        return None

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=cfg.get("anthropic_model") or "claude-sonnet-5",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def _rewrite_with_openai(cfg, prompt):
    try:
        from openai import OpenAI
    except ImportError:
        print("[ai_content] `openai` not installed. Run: pip install openai")
        return None

    api_key = cfg.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[ai_content] No OpenAI API key provided.")
        return None

    client = OpenAI(api_key=api_key)
    model = cfg.get("openai_model") or "gpt-4o-mini"
    try:
        resp = client.responses.create(
            model=model,
            input=prompt,
            max_output_tokens=16000,
        )
        return resp.output_text.strip()
    except Exception as responses_error:
        print(f"[ai_content] OpenAI Responses API failed ({responses_error}); trying Chat Completions.")
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=12000,
            )
            return resp.choices[0].message.content.strip()
        except Exception as chat_error:
            message = str(chat_error)
            if "Connection error" in message:
                raise RuntimeError(
                    "OpenAI connection failed. The local server cannot reach api.openai.com. "
                    "Check internet/VPN/firewall, then restart the Flask app with network access."
                ) from chat_error
            raise


def rewrite_sections_with_ai(cfg, sections):
    """Returns rewritten sections, or original sections if AI is unavailable."""
    texts = _extract_text_map(sections)
    if not texts:
        return sections

    prompt = _build_prompt(cfg, texts)
    provider = (cfg.get("ai_provider") or "anthropic").lower()

    try:
        raw = _rewrite_with_openai(cfg, prompt) if provider == "openai" else _rewrite_with_anthropic(cfg, prompt)
        if not raw:
            raise RuntimeError(f"{provider} did not return rewritten text. Check API key and package setup.")
        raw = raw.replace("```json", "").replace("```", "").strip()
        new_texts = json.loads(raw)
        for key, value in texts.items():
            new_texts.setdefault(key, value)
        return _apply_text_map(sections, new_texts)
    except Exception as e:
        if cfg.get("fail_on_ai_error"):
            raise
        print(f"[ai_content] AI rewrite failed ({e}) - keeping template copy.")
        return sections
