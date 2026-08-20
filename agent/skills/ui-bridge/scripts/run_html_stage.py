"""
Advance one page through the HTML pipeline.

The generator follows the shared Phase 0 prototype contract:
- `ui-prototypes/design-tokens.css` is the shared token source
- every page copies the required core tokens inline in `:root`
- public/admin shared chrome is stamped through `_partials/`
- homepage/index pages receive a richer storefront treatment instead of generic filler
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from ui_bridge_core import ApprovalStore, ensure_bridge, read_json, utc_now, write_json


STAGES = [
    "skeleton",
    "content",
    "layout",
    "styling",
    "interactions",
    "accessibility",
    "anti-slop",
    "reviewers",
]

FILES = {
    "skeleton": "01-skeleton.html",
    "content": "02-content.html",
    "layout": "03-layout.html",
    "styling": "04-styling.html",
    "interactions": "05-interactions.html",
    "accessibility": "06-accessibility.html",
    "anti-slop": "07-anti-slop-candidate.html",
    "reviewers": "08-reviewed-final-candidate.html",
}


def latest(root: Path, name: str) -> Dict:
    bridge = ensure_bridge(root)
    latest_map = read_json(bridge / "latest.json", default={}) or {}
    filename = latest_map.get(name)
    if filename:
        return read_json(bridge / filename, default={}) or {}
    return {}


def page_record(root: Path, slug: str) -> Dict:
    page_map = read_json(ensure_bridge(root) / "page-map.json", default={}) or {}
    for page in page_map.get("pages", []):
        if page.get("slug") == slug:
            return page
    raise SystemExit(f"ERROR: page {slug} not found in page-map.json")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def design_system(root: Path) -> Dict[str, Any]:
    return read_json(ensure_bridge(root) / "design-system.json", default={}) or {}


def token_values(root: Path) -> Dict[str, str]:
    token_file = root / "ui-prototypes" / "design-tokens.css"
    default = {
        "--color-primary": "#243D36",
        "--color-accent": "#8A4D76",
        "--color-bg": "#FFFFFF",
        "--font-heading": "'system-ui', sans-serif",
        "--font-body": "'system-ui', sans-serif",
        "--text-h1": "clamp(2.4rem, 6vw, 5.4rem)",
        "--space-4": "1rem",
        "--radius-md": "1rem",
        "--duration-base": "220ms",
        "--ease-primary": "cubic-bezier(0.22, 1, 0.36, 1)",
    }
    if not token_file.exists():
        return default
    text = token_file.read_text(encoding="utf-8", errors="ignore")
    values = dict(default)
    for key in list(values):
        match = re.search(rf"{re.escape(key)}\s*:\s*([^;]+);", text)
        if match:
            values[key] = match.group(1).strip()
    return values


def project_name(root: Path) -> str:
    spec = (design_system(root).get("spec") or {})
    return spec.get("project_name") or "UI Prototype"


def page_kind(page: Dict[str, Any]) -> str:
    slug = page.get("slug", "")
    if page.get("is_admin"):
        if "login" in slug:
            return "admin-login"
        if "detail" in slug:
            return "admin-detail"
        return "admin-list"
    if slug in ("index", "home"):
        return "home"
    if "course" in slug or "category" in slug:
        return "catalog"
    if "product" in slug:
        return "product"
    if "checkout" in slug:
        return "checkout"
    if "account" in slug or "auth" in slug:
        return "account"
    if "faq" in slug:
        return "faq"
    return "content"


def realistic_content(page: Dict[str, Any], root: Path) -> Dict[str, Any]:
    brand = project_name(root)
    kind = page_kind(page)
    if page.get("direction", "ltr") == "rtl":
        base = {
            "brand": brand,
            "skip": "تجاوز إلى المحتوى الرئيسي",
            "cta": "اطلب عرض النموذج",
            "secondary_cta": "استعرض التشكيلات",
            "footer": "مرجع بصري معتمد لمرحلة التصميم قبل التنفيذ.",
        }
    else:
        base = {
            "brand": brand,
            "skip": "Skip to main content",
            "cta": "Request prototype review",
            "secondary_cta": "Explore featured collections",
            "footer": "Approved visual reference for the design phase before engineering starts.",
        }

    if kind == "home":
        base.update(
            {
                "headline": "A calmer storefront with stronger product storytelling",
                "lede": "Turn the homepage into a client-facing sales surface with curated collections, premium product framing, and faster paths to checkout.",
                "hero_media_label": "Featured storefront composition",
                "feature_tiles": [
                    {"eyebrow": "Merchandising", "title": "Curated product focus", "detail": "Show fewer, better-framed categories so the client sees a clear point of view instead of a crowded grid."},
                    {"eyebrow": "Conversion", "title": "Reduced friction", "detail": "Use a visible path from discovery to product detail to cart, supported by trust messaging instead of noise."},
                    {"eyebrow": "Brand tone", "title": "Premium but usable", "detail": "Editorial spacing, controlled color contrast, and confident CTA placement make the page feel intentional."},
                ],
                "category_cards": [
                    {"name": "Kitchen essentials", "caption": "High-rotation products presented with premium editorial cropping."},
                    {"name": "Daily wellness", "caption": "Personal-use favorites grouped by routine rather than only price."},
                    {"name": "Gift-ready bundles", "caption": "Higher-consideration sets surfaced with stronger story value."},
                ],
                "product_cards": [
                    {"name": "Stoneware Brew Set", "price": "$68", "meta": "Best seller · Ships in 24h"},
                    {"name": "Minimal Pantry Rack", "price": "$124", "meta": "Bundle eligible · Low stock"},
                    {"name": "Canvas Market Tote", "price": "$34", "meta": "New season · Gift-ready"},
                ],
                "items": [
                    {"title": "Hero composition", "meta": "Brand story and featured products", "detail": "The first screen should explain what kind of store this is and why the products feel worth exploring."},
                    {"title": "Collection discovery", "meta": "Category-to-product path", "detail": "Collection rails should make browsing feel guided instead of purely utilitarian."},
                    {"title": "Purchase confidence", "meta": "Delivery, trust, and policy cues", "detail": "Support conversion with reassurance that feels integrated into the design, not bolted on."},
                ],
            }
        )
    elif kind == "catalog":
        base.update(
            {
                "headline": "Category pages shaped around comparison and confidence",
                "lede": "Use the category view to help customers scan quickly, compare meaningfully, and move into product details with less hesitation.",
                "items": [
                    {"title": "Collection framing", "meta": "Lead with merchandising logic", "detail": "Use category descriptions and filtering cues that feel tied to real shopping intent."},
                    {"title": "Product card system", "meta": "Readable at a glance", "detail": "Cards should balance image space, pricing hierarchy, and utility actions without becoming visually repetitive."},
                    {"title": "Trust support", "meta": "Policies and delivery signals", "detail": "Subtle delivery and stock context can increase confidence without interrupting the browse flow."},
                ],
            }
        )
    elif kind == "product":
        base.update(
            {
                "headline": "Product detail pages that feel persuasive, not template-driven",
                "lede": "The product page should present imagery, pricing, delivery promise, and purchase logic as one clear narrative.",
                "items": [
                    {"title": "Product gallery", "meta": "High-confidence visual hierarchy", "detail": "Hero imagery should feel premium even before final photography is supplied."},
                    {"title": "Decision content", "meta": "Specs, reassurance, and urgency", "detail": "Use detail blocks that help a shopper decide, not just fill the page with generic tabs."},
                    {"title": "Purchase support", "meta": "Related items and service cues", "detail": "Cross-sell and trust cues should reinforce the purchase moment rather than dilute it."},
                ],
            }
        )
    elif kind == "checkout":
        base.update(
            {
                "headline": "Checkout layouts built for clarity and completion",
                "lede": "Treat checkout as a confidence surface with a clean review column, clear totals, and minimal distraction.",
                "items": [
                    {"title": "Order review", "meta": "Readable summary panel", "detail": "Keep product, quantity, shipping, and pricing visible without making the layout feel dense."},
                    {"title": "Form clarity", "meta": "Field grouping and progress cues", "detail": "Shipping, payment, and confirmation sections should read as a calm sequence."},
                    {"title": "Trust reinforcement", "meta": "Policy and support context", "detail": "A few well-placed reassurance elements can do more than a wall of badges."},
                ],
            }
        )
    elif kind == "admin-list":
        base.update(
            {
                "headline": "Operations workspace for approved UI-first delivery",
                "lede": "Use the prototype to validate tables, filters, actions, and layout rhythm before implementation work begins.",
                "items": [
                    {"title": "Filter state", "meta": "Status, owner, and date filters", "detail": "Every control is represented as static approved UI before wiring APIs."},
                    {"title": "Primary table", "meta": "Real columns and row density", "detail": "Table structure mirrors the tasks and page map for the page."},
                    {"title": "Action rail", "meta": "Topbar actions and shortcuts", "detail": "Quick actions stay consistent through the shared sidebar shell."},
                ],
            }
        )
    else:
        base.update(
            {
                "headline": "Approved page prototype for client-facing review",
                "lede": "This page is produced as part of UI Phase 0 and should be reviewed before code implementation moves ahead.",
                "items": [
                    {"title": "Page hero", "meta": "Message and visual hierarchy", "detail": "Headline, supporting copy, and call to action reflect the approved direction."},
                    {"title": "Main content", "meta": "Section ordering from page map", "detail": "Sections follow the exact planning sequence rather than a generic template order."},
                    {"title": "Implementation reference", "meta": "Tokens, partials, and navigation", "detail": "The page shares the same token system and shell conventions as the rest of the prototype set."},
                ],
            }
        )
    return base


def page_links(root: Path) -> list[dict]:
    page_map = read_json(ensure_bridge(root) / "page-map.json", default={}) or {}
    return page_map.get("pages", [])


def prototype_nav(root: Path, current_slug: str) -> str:
    links = []
    for page in page_links(root):
        slug = page.get("slug")
        label = page.get("name", slug)
        cls = ' class="current"' if slug == current_slug else ""
        links.append(f'<a href="{slug}.html"{cls}>{label}</a>')
    links.append('<a href="prototype-hub.html">Prototype Hub</a>')
    return '<nav class="prototype-nav" aria-label="Prototype navigation" dir="ltr">' + " ".join(links) + "</nav>"


def shared_shell_markers(page: Dict[str, Any]) -> str:
    if page.get("is_admin"):
        return (
            '<div class="admin-shell">'
            '<aside class="sidebar" aria-label="Main navigation"><!-- PARTIAL:sidebar-admin -->\n<!-- /PARTIAL:sidebar-admin --></aside>'
            '<div class="admin-main"><div class="topbar container"><p>Approved admin shell</p></div>'
        )
    return '<header class="site-shell-header"><!-- PARTIAL:nav-public -->\n<!-- /PARTIAL:nav-public --></header>'


def shared_shell_close(page: Dict[str, Any]) -> str:
    if page.get("is_admin"):
        return "</div></div>"
    return '<footer class="site-shell-footer"><!-- PARTIAL:footer-public -->\n<!-- /PARTIAL:footer-public --></footer>'


def render_items(items: List[Dict[str, str]]) -> str:
    return "".join(
        "<article class=\"content-row\"><span class=\"row-mark\" aria-hidden=\"true\"></span><div>"
        f"<h3>{esc(item['title'])}</h3><p class=\"row-meta\">{esc(item['meta'])}</p><p>{esc(item['detail'])}</p></div></article>"
        for item in items
    )


def home_feature_tiles(items: List[Dict[str, str]]) -> str:
    return "".join(
        '<article class="feature-tile">'
        f'<span>{esc(item["eyebrow"])}</span>'
        f'<h3>{esc(item["title"])}</h3>'
        f'<p>{esc(item["detail"])}</p>'
        "</article>"
        for item in items
    )


def category_cards(items: List[Dict[str, str]]) -> str:
    return "".join(
        '<article class="collection-card"><div class="collection-visual" aria-hidden="true"></div>'
        f'<h3>{esc(item["name"])}</h3><p>{esc(item["caption"])}</p></article>'
        for item in items
    )


def product_cards(items: List[Dict[str, str]]) -> str:
    return "".join(
        '<article class="product-card"><div class="product-image" aria-hidden="true"></div>'
        f'<p class="product-meta">{esc(item["meta"])}</p>'
        f'<h3>{esc(item["name"])}</h3><strong>{esc(item["price"])}</strong>'
        '<a href="#" class="product-link">View product</a></article>'
        for item in items
    )


def home_sections(content: Dict[str, Any]) -> str:
    feature_tiles = home_feature_tiles(content.get("feature_tiles", []))
    collections = category_cards(content.get("category_cards", []))
    products = product_cards(content.get("product_cards", []))
    return f"""
      <section class="feature-strip" aria-label="Storefront advantages">
        {feature_tiles}
      </section>
      <section class="showcase-band" id="collections">
        <div class="section-copy">
          <p class="section-kicker">Collection focus</p>
          <h2>Browse the store the way a client will understand it</h2>
          <p>Group products into visually distinct collection cards so the homepage communicates structure, quality, and range before a customer scrolls far.</p>
        </div>
        <div class="collection-grid">
          {collections}
        </div>
      </section>
      <section class="product-band">
        <div class="section-copy">
          <p class="section-kicker">Featured products</p>
          <h2>Make product cards feel premium, not boilerplate</h2>
        </div>
        <div class="product-grid">
          {products}
        </div>
      </section>
"""


def inline_root_tokens(root: Path) -> str:
    values = token_values(root)
    return "\n".join(
        [
            ":root {",
            f"  --color-primary: {values['--color-primary']};",
            f"  --color-accent: {values['--color-accent']};",
            f"  --color-bg: {values['--color-bg']};",
            f"  --font-heading: {values['--font-heading']};",
            f"  --font-body: {values['--font-body']};",
            f"  --text-h1: {values['--text-h1']};",
            f"  --space-4: {values['--space-4']};",
            f"  --radius-md: {values['--radius-md']};",
            f"  --duration-base: {values['--duration-base']};",
            f"  --ease-primary: {values['--ease-primary']};",
            "}",
        ]
    )


def full_document(root: Path, page: Dict[str, Any], artifacts: Dict[str, Dict], draft: bool = False) -> str:
    content = realistic_content(page, root)
    slug = page["slug"]
    layout = artifacts["layout-dna"].get("page_assignments", {}).get(slug, {})
    hero = artifacts["hero-diversity"].get("page_assignments", {}).get(slug, "proof-first")
    narrative = artifacts["narrative-patterns"].get("page_assignments", {}).get(slug, "authority")
    section_pattern = artifacts["section-diversity"].get("page_assignments", {}).get(slug, "proof-strip")
    watermark = '<div class="draft-watermark">UNAPPROVED DRAFT PROTOTYPE</div>' if draft else ""
    shell_open = shared_shell_markers(page)
    shell_close = shared_shell_close(page)
    proto_nav = prototype_nav(root, slug)
    direction = page.get("direction", "ltr")
    is_home = page_kind(page) == "home"
    secondary_href = "#collections" if is_home else "prototype-hub.html"
    extra_sections = home_sections(content) if is_home else ""
    hero_media = (
        f'<div class="hero-media" aria-label="{esc(content.get("hero_media_label", "Featured product preview"))}">'
        '<div class="hero-media-panel panel-large"><span>Editorial hero product</span><strong>Premium storefront composition</strong></div>'
        '<div class="hero-media-stack"><div class="hero-media-panel panel-small"><span>Category focus</span></div><div class="hero-media-panel panel-small accent"><span>Fast checkout promise</span></div></div>'
        '</div>'
        if is_home
        else '<aside class="proof-list" aria-label="Proof panel"><span>Page map guided layout</span><span>Token-driven styling</span><span>Phase 0 approved reference</span></aside>'
    )
    return f"""<!DOCTYPE html>
<html lang="{esc('ar' if direction == 'rtl' else 'en')}" dir="{esc(direction)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(page.get("name", slug))}</title>
  <link rel="stylesheet" href="design-tokens.css">
  <style>
    {inline_root_tokens(root)}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--color-bg); color: var(--color-text-primary, #1F2724); font-family: var(--font-body); line-height: 1.7; }}
    a {{ color: inherit; text-decoration: none; transition: color var(--duration-base) var(--ease-primary); }}
    .skip-link {{ position: absolute; inset-inline-start: 16px; top: -48px; background: var(--color-primary); color: white; padding: 10px 14px; z-index: 20; }}
    .skip-link:focus {{ top: 12px; }}
    .draft-watermark {{ position: sticky; top: 0; z-index: 30; background: #111; color: #fff; text-align: center; padding: 8px; font-weight: 700; }}
    .hero {{ display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(300px, .85fr); gap: clamp(28px, 5vw, 72px); align-items: end; padding: clamp(56px, 8vw, 112px) 0 clamp(32px, 6vw, 72px); }}
    .context-line, .row-meta {{ color: var(--color-accent); font-weight: 800; margin: 0 0 8px; }}
    .section-kicker {{ color: var(--color-accent); text-transform: uppercase; letter-spacing: .12em; font-size: .76rem; font-weight: 800; margin: 0 0 10px; }}
    h1, h2, h3 {{ font-family: var(--font-heading); line-height: 1.15; margin: 0; }}
    h1 {{ font-size: var(--text-h1); max-width: 11ch; }}
    h2 {{ font-size: var(--text-h2, clamp(1.8rem, 3.5vw, 2.8rem)); margin-bottom: var(--space-4); }}
    .lede {{ max-width: 64ch; font-size: 1.08rem; color: var(--color-text-secondary, #53615C); }}
    .hero-actions {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 28px; }}
    .button {{ display: inline-flex; align-items: center; justify-content: center; min-height: 42px; padding: 0 18px; border: 1px solid var(--color-primary); border-radius: var(--radius-md); font-weight: 700; }}
    .button.primary {{ background: var(--color-primary); color: #fff; }}
    .button.secondary {{ background: transparent; color: var(--color-primary); }}
    .proof-list {{ background: var(--color-surface, #F4F2EC); border-top: 2px solid var(--color-accent); padding: 24px; display: grid; gap: 12px; border-radius: var(--radius-md); box-shadow: var(--shadow-card, 0 20px 50px rgba(12,22,19,.08)); }}
    .proof-list span {{ border-bottom: 1px solid var(--color-border, #D7DCD8); padding-bottom: 10px; font-weight: 700; }}
    .hero-media {{ display: grid; gap: 16px; align-self: stretch; }}
    .hero-media-panel {{ border-radius: calc(var(--radius-md) * 1.5); padding: 24px; min-height: 180px; box-shadow: var(--shadow-card, 0 20px 50px rgba(12,22,19,.08)); display: flex; flex-direction: column; justify-content: end; background: linear-gradient(135deg, color-mix(in srgb, var(--color-primary) 18%, white), rgba(255,255,255,.9)); border: 1px solid color-mix(in srgb, var(--color-primary) 10%, white); }}
    .hero-media-panel.accent {{ background: linear-gradient(135deg, color-mix(in srgb, var(--color-accent) 18%, white), rgba(255,255,255,.88)); border-color: color-mix(in srgb, var(--color-accent) 12%, white); }}
    .hero-media-panel span {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .12em; color: var(--color-accent); font-weight: 800; }}
    .hero-media-panel strong {{ margin-top: 12px; font-size: 1.35rem; font-family: var(--font-heading); max-width: 12ch; }}
    .hero-media-stack {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
    .feature-strip {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 12px; }}
    .feature-tile {{ background: #fff; border: 1px solid var(--color-border, #D7DCD8); border-radius: var(--radius-md); padding: 22px; box-shadow: var(--shadow-card, 0 20px 50px rgba(12,22,19,.08)); }}
    .feature-tile span {{ display: inline-block; font-size: .76rem; text-transform: uppercase; letter-spacing: .1em; color: var(--color-accent); font-weight: 800; margin-bottom: 10px; }}
    .feature-tile h3 {{ margin-bottom: 10px; font-size: 1.1rem; }}
    .feature-tile p {{ margin: 0; color: var(--color-text-secondary, #53615C); }}
    .content-band {{ padding: clamp(40px, 7vw, 96px) 0; }}
    .content-grid {{ background: #fff; border: 1px solid var(--color-border, #D7DCD8); border-radius: var(--radius-md); overflow: hidden; box-shadow: var(--shadow-card, 0 20px 50px rgba(12,22,19,.08)); }}
    .content-row {{ display: grid; grid-template-columns: 18px minmax(0, 1fr); gap: 20px; padding: 24px; border-bottom: 1px solid var(--color-border, #D7DCD8); }}
    .content-row:last-child {{ border-bottom: 0; }}
    .row-mark {{ width: 10px; height: 10px; margin-top: .45rem; background: var(--color-accent); display: inline-block; }}
    .showcase-band, .product-band {{ padding: clamp(40px, 7vw, 90px) 0; }}
    .section-copy {{ display: grid; gap: 8px; margin-bottom: 22px; max-width: 58ch; }}
    .section-copy p:last-child {{ margin: 0; color: var(--color-text-secondary, #53615C); }}
    .collection-grid, .product-grid {{ display: grid; gap: 18px; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .collection-card, .product-card {{ background: #fff; border: 1px solid var(--color-border, #D7DCD8); border-radius: calc(var(--radius-md) * 1.25); padding: 18px; box-shadow: var(--shadow-card, 0 20px 50px rgba(12,22,19,.08)); }}
    .collection-visual, .product-image {{ border-radius: calc(var(--radius-md) * 1.1); min-height: 180px; margin-bottom: 16px; background: linear-gradient(160deg, color-mix(in srgb, var(--color-primary) 14%, white), color-mix(in srgb, var(--color-accent) 12%, white)); }}
    .product-image {{ min-height: 220px; background: linear-gradient(160deg, color-mix(in srgb, var(--color-surface, #F3F6F4) 72%, white), color-mix(in srgb, var(--color-primary) 10%, white)); }}
    .collection-card h3, .product-card h3 {{ margin-bottom: 8px; font-size: 1.12rem; }}
    .collection-card p, .product-card p {{ margin: 0; color: var(--color-text-secondary, #53615C); }}
    .product-card strong {{ display: block; margin-top: 12px; font-size: 1.4rem; font-family: var(--font-heading); }}
    .product-meta {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; color: var(--color-accent); font-weight: 800; margin-bottom: 10px !important; }}
    .product-link {{ display: inline-flex; margin-top: 14px; color: var(--color-primary); font-weight: 700; }}
    .cta-section {{ padding: clamp(36px, 6vw, 76px) 0; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 24px; align-items: center; }}
    .page-main {{ padding-bottom: var(--space-12); }}
    .topbar {{ padding-top: var(--space-6); }}
    @media (max-width: 768px) {{
      .hero, .cta-section {{ grid-template-columns: 1fr; }}
      .hero-media-stack, .feature-strip, .collection-grid, .product-grid {{ grid-template-columns: 1fr; }}
      h1 {{ max-width: 100%; }}
      .content-row {{ grid-template-columns: 1fr; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{ animation-duration: .01ms !important; transition-duration: .01ms !important; }}
    }}
  </style>
</head>
<body class="{'admin-body' if page.get('is_admin') else 'public-body'}">
  <a class="skip-link" href="#main">{esc(content['skip'])}</a>
  {watermark}
  {shell_open}
  <main id="main" class="page-main">
    <div class="container">
      <section class="hero" data-page="{esc(slug)}" data-layout="{esc(layout.get('layout_pattern', 'editorial-index'))}" data-hero="{esc(hero)}" data-narrative="{esc(narrative)}">
        <div class="hero-copy">
          <p class="context-line">{esc(narrative)}</p>
          <h1>{esc(content['headline'])}</h1>
          <p class="lede">{esc(content['lede'])}</p>
          <div class="hero-actions">
            <a class="button primary" href="#cta">{esc(content['cta'])}</a>
            <a class="button secondary" href="{secondary_href}">{esc(content['secondary_cta'])}</a>
          </div>
        </div>
        {hero_media}
      </section>
      {extra_sections}
      <section class="content-band" data-section-pattern="{esc(section_pattern)}">
        <h2>{esc(page.get("name", slug))}</h2>
        <div class="content-grid">
          {render_items(content['items'])}
        </div>
      </section>
      <section id="cta" class="cta-section">
        <div>
          <h2>Shared implementation reference</h2>
          <p>This page keeps color, typography, spacing, and motion in shared variables so the full feature can be re-themed safely later.</p>
        </div>
        <a class="button primary" href="mailto:prototype@example.com" aria-label="{esc(content['cta'])}">{esc(content['cta'])}</a>
      </section>
    </div>
  </main>
  {shell_close}
  {proto_nav}
  <div class="proto-spacer" aria-hidden="true"></div>
  <script type="application/json" id="ui-stage-data">{esc(json.dumps({"page": slug, "hero_pattern": hero, "narrative_pattern": narrative}, ensure_ascii=False))}</script>
  <script>
    document.documentElement.dataset.stage = "interactions";
    document.querySelectorAll(".button").forEach(function(el) {{
      el.addEventListener("click", function() {{
        document.documentElement.dataset.intent = "cta";
      }});
    }});
  </script>
</body>
</html>
"""


def blocking_html_issues(text: str) -> List[str]:
    issues = []
    if "<!DOCTYPE html>" not in text:
        issues.append("document missing <!DOCTYPE html>")
    if '<main id="main"' not in text:
        issues.append("main landmark missing")
    if 'class="container"' not in text:
        issues.append("container wrapper missing")
    if 'class="prototype-nav"' not in text:
        issues.append("prototype nav missing")
    if "design-tokens.css" not in text:
        issues.append("shared token stylesheet link missing")
    for token in [
        "--color-primary",
        "--color-accent",
        "--color-bg",
        "--font-heading",
        "--font-body",
        "--text-h1",
        "--space-4",
        "--radius-md",
        "--duration-base",
        "--ease-primary",
    ]:
        if token not in text:
            issues.append(f"required token missing: {token}")
    for phrase in ("TODO", "REPLACE_ME", "[PLACEHOLDER]", "John Doe", "Company Name"):
        if phrase.lower() in text.lower():
            issues.append(f"placeholder content remains: {phrase}")
    return issues


def stage_body(root: Path, stage: str, previous: str, page: Dict, artifacts: Dict[str, Dict]) -> str:
    if stage == "skeleton":
        direction = page.get("direction", "ltr")
        shell_open = shared_shell_markers(page)
        shell_close = shared_shell_close(page)
        return f"""<!DOCTYPE html>
<html lang="{('ar' if direction == 'rtl' else 'en')}" dir="{direction}">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{esc(page.get("name", page["slug"]))}</title><link rel="stylesheet" href="design-tokens.css"><style>{inline_root_tokens(root)}</style></head>
<body>{shell_open}<main id="main" class="page-main"><div class="container"></div></main>{shell_close}{prototype_nav(root, page["slug"])}<div class="proto-spacer" aria-hidden="true"></div></body>
</html>
"""
    if stage == "content":
        return full_document(root, page, artifacts, draft=False)
    if stage == "layout":
        return previous.replace('<main id="main" class="page-main">', '<main id="main" class="page-main" data-layout-reviewed="true">', 1)
    if stage == "styling":
        return previous.replace("</head>", '<meta name="ui-stage" content="styling-complete"></head>', 1)
    if stage == "interactions":
        if "document.documentElement.dataset.intent" in previous:
            return previous
        return previous.replace("</body>", '<script>document.querySelectorAll(".button").forEach(function(el){el.addEventListener("click",function(){document.documentElement.dataset.intent="cta";});});</script></body>')
    if stage == "accessibility":
        return previous.replace("<html ", '<html data-accessibility-reviewed="true" ', 1)
    if stage == "anti-slop":
        issues = blocking_html_issues(previous)
        if issues:
            raise SystemExit("ERROR: anti-slop HTML stage blocked: %s" % "; ".join(issues))
        return "<!-- anti-slop candidate: blocking checks passed -->\n" + previous
    if stage == "reviewers":
        issues = blocking_html_issues(previous)
        if issues:
            raise SystemExit("ERROR: reviewer HTML stage blocked: %s" % "; ".join(issues))
        return "<!-- reviewed final candidate: Phase 0 checks passed -->\n" + previous
    return previous


def main() -> None:
    parser = argparse.ArgumentParser(description="Advance one HTML stage")
    parser.add_argument("--root", default=".")
    parser.add_argument("--page", required=True)
    parser.add_argument("--stage", choices=STAGES, required=True)
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not args.draft:
        missing = ApprovalStore(root).require(["brand_direction", "moodboard", "visual_layout_dna", "design_system"])
        if missing:
            print("ERROR: approval gate failed before stage generation. Missing: %s" % ", ".join(missing), file=sys.stderr)
            sys.exit(1)

    bridge = ensure_bridge(root)
    page = page_record(root, args.page)
    page_dir = bridge / "html-stages" / args.page
    page_dir.mkdir(parents=True, exist_ok=True)

    index = STAGES.index(args.stage)
    previous = ""
    if index > 0:
        previous_path = page_dir / FILES[STAGES[index - 1]]
        if not previous_path.exists():
            raise SystemExit(f"ERROR: previous stage missing: {previous_path}")
        previous = previous_path.read_text(encoding="utf-8", errors="ignore")

    artifacts = {
        "layout-dna": latest(root, "layout-dna"),
        "hero-diversity": latest(root, "hero-diversity"),
        "narrative-patterns": latest(root, "narrative-patterns"),
        "section-diversity": latest(root, "section-diversity"),
        "content-realism": latest(root, "content-realism"),
    }
    out = page_dir / FILES[args.stage]
    if args.stage == "content":
        rendered = full_document(root, page, artifacts, draft=args.draft)
    else:
        rendered = stage_body(root, args.stage, previous, page, artifacts)
    out.write_text(rendered, encoding="utf-8")
    write_json(
        page_dir / "stage-state.json",
        {
            "slug": args.page,
            "current_stage": args.stage,
            "stage_file": out.name,
            "updated_at": utc_now(),
            "draft": args.draft,
        },
    )
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
