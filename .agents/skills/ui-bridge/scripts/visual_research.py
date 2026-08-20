"""
Visual research engine: real product references, pattern guidance only.

Policy: this module supplies real product names and design pattern observations.
It must NEVER supply category color palettes, category font pairings, or
ready-made brand tokens — those must come from approved brand signals only.
"""
from __future__ import annotations

import json
from typing import Dict, List


# Real product references per category — what to study and why.
# No colors, no fonts. Study structure, hierarchy, and copywriting patterns only.
_REFERENCES: Dict[str, Dict] = {
    "EdTech": {
        "top_3_products": [
            {
                "name": "Coursera",
                "url": "coursera.org",
                "what_to_study": "Social proof placement: partner logos, learner counts, and outcome stats. Note how they sequence trust before CTA.",
            },
            {
                "name": "80,000 Hours",
                "url": "80000hours.org",
                "what_to_study": "Editorial narrative flow: long-form sections with article-like rhythm, evidence-first copy, and zero equal-card grids.",
            },
            {
                "name": "Kajabi",
                "url": "kajabi.com",
                "what_to_study": "Instructor authority pattern: named expert photo, short bio line, and course cards that lead with the instructor, not the price.",
            },
        ],
        "top_3_inspo_sites": [
            {
                "name": "Harvard Online (online.harvard.edu)",
                "what_to_study": "Institutional credibility without decoration: clean typography, proof by affiliation, asymmetric feature blocks.",
            },
            {
                "name": "Outlier.org",
                "what_to_study": "Minimalist academic feel: generous whitespace, serif-weight headlines for authority, outcome proof in two lines, no hero image required.",
            },
            {
                "name": "Luma.id",
                "what_to_study": "Event/cohort page rhythm: date prominence, speaker credibility, scarcity-aware CTA copy ('Registration closes…').",
            },
        ],
    },
    "EdTech_Arabic": {
        "top_3_products": [
            {
                "name": "Coursera Arabic",
                "url": "coursera.org/ar",
                "what_to_study": "RTL proof layout: how partner logos, stats, and social proof reorder naturally in Arabic reading direction without feeling mirrored.",
            },
            {
                "name": "Udemy Arabic (ar.udemy.com)",
                "url": "ar.udemy.com",
                "what_to_study": "Course card density for RTL: title width, rating placement, price position. Notice what gets truncated and design around it.",
            },
            {
                "name": "Rwaq (rwaq.org)",
                "url": "rwaq.org",
                "what_to_study": "Arabic-first EdTech with institutional tone: heading weight, section dividers, and how they handle hero copy in Arabic without it feeling cramped.",
            },
        ],
        "top_3_inspo_sites": [
            {
                "name": "Madrasa.com",
                "what_to_study": "Clean Arabic educational UI: navigation depth, breadcrumb handling in RTL, and how they separate public catalog from learner dashboard.",
            },
            {
                "name": "Alison.com Arabic",
                "what_to_study": "Certificate proof pattern: how credentials are displayed prominently to Arabic audiences where credentials carry high social weight.",
            },
            {
                "name": "Linear.app (for admin surfaces)",
                "what_to_study": "Dense admin table design: scan-friendly layout, status badges, inline actions. Apply this pattern to the Arabic CRM admin side (admin stays LTR).",
            },
        ],
    },
    "Marketing/CRM": {
        "top_3_products": [
            {
                "name": "HubSpot Marketing Hub",
                "url": "hubspot.com",
                "what_to_study": "Lead capture flow: how they move from value statement to form without a hard sell. Notice the minimal friction between hero and first CTA.",
            },
            {
                "name": "Notion marketing site",
                "url": "notion.so",
                "what_to_study": "Feature proof via screenshots: real product in context beats illustrated diagrams. Density control between feature rows.",
            },
            {
                "name": "Attio CRM",
                "url": "attio.com",
                "what_to_study": "Modern CRM admin aesthetic: data table design, filter bar patterns, status chip design, and empty state illustrations.",
            },
        ],
        "top_3_inspo_sites": [
            {
                "name": "Stripe.com",
                "what_to_study": "Trust through precision: exact copy ('99.999% uptime'), micro-typography tightness, and how a single well-placed number beats a paragraph.",
            },
            {
                "name": "Linear.app",
                "what_to_study": "Admin interface density: how to make complex data tables feel calm, not chaotic. Column sizing, row hover states, and action menus.",
            },
            {
                "name": "Brevo (ex-Sendinblue)",
                "what_to_study": "Registration and contact form UX: field grouping, inline validation messaging, and confirmation state design.",
            },
        ],
    },
}

_DEFAULT_REFERENCES = {
    "top_3_products": [
        {"name": "Category leader in your domain", "what_to_study": "Information hierarchy and trust proof placement"},
        {"name": "Operational/admin tool in your domain", "what_to_study": "Dense forms, tables, filters, and admin ergonomics"},
        {"name": "Editorial reference in your domain", "what_to_study": "Story rhythm, proof placement, and reading flow"},
    ],
    "top_3_inspo_sites": [
        {"name": "Top editorial site in your category", "what_to_study": "Article-like sections and expert credibility signals"},
        {"name": "Enterprise tool in your category", "what_to_study": "Partner proof and conversion path"},
        {"name": "Admin-heavy product surface", "what_to_study": "Compact controls and scan-friendly data layout"},
    ],
}

_VISUAL_DNA: Dict[str, Dict] = {
    "EdTech": {
        "must_do": [
            "vary hero structure per page purpose: home uses proof-first, course detail uses evidence-led split, admin uses compact table-first",
            "lead with a named expert or real cohort photo — no anonymous stock classroom images",
            "keep admin screens compact and scannable: tight row height, status chips, inline actions",
            "sequence trust before CTA: show proof (alumni, partners, outcomes) before asking for registration",
            "use Arabic-first copy in public pages; admin stays LTR",
        ],
        "must_not_do": [
            "do not start every section with a centered h2 + three equal cards — break this pattern at least 3 times per page",
            "do not use fake round numbers: '500+ students', '99% satisfaction', '24/7 support' — use real or omit",
            "do not use anonymous stock photos of people smiling at laptops",
            "do not use premade category color palettes — derive all colors from approved brand signals",
            "do not use premade category font pairings — use only approved project fonts",
            "do not repeat the same section structure on adjacent sections of the same page",
        ],
    },
    "EdTech_Arabic": {
        "must_do": [
            "all public pages are RTL by default (lang=ar, dir=rtl)",
            "admin panel uses LTR layout even on Arabic projects — admins work with data entry tools LTR",
            "vary hero structures: home gets editorial asymmetric, course detail gets split-screen, experts page gets person-led",
            "keep registration form prominent but not pushy: embed it in context, not as a modal pop-over",
            "use real Arabic copy — never translate English placeholder copy literally",
        ],
        "must_not_do": [
            "do not mirror the layout visually (just flip CSS direction, do not reverse every component)",
            "do not use fake Arabic names or placeholder metrics",
            "do not use category color palettes — derive all colors from approved brand direction",
            "do not use category font pairings — use only the approved project fonts",
            "do not stack centered hero + equal three-card grid — vary hero and section patterns",
        ],
    },
}

_DEFAULT_DNA = {
    "must_do": [
        "vary hero structures by page purpose",
        "use page-specific narrative patterns",
        "keep admin screens dense and utilitarian",
        "separate public RTL and admin LTR decisions",
    ],
    "must_not_do": [
        "do not use category color palettes",
        "do not use category font pairings",
        "do not repeat centered hero plus equal-card grid",
        "do not use fake metrics or placeholder people",
    ],
}


class VisualResearchEngine:
    def get_research_references(self, project_category: str) -> Dict:
        refs = _REFERENCES.get(project_category, _DEFAULT_REFERENCES)
        return {
            "project_category": project_category,
            "research_policy": "real_product_references_no_premade_tokens",
            "top_3_products": refs["top_3_products"],
            "top_3_inspo_sites": refs["top_3_inspo_sites"],
            "token_policy": {
                "colors": "derive only from approved brand direction or generated proposal artifact",
                "fonts": "derive only from approved brand direction or explicit project font signals",
            },
        }

    def generate_visual_dna(self, project_category: str) -> Dict:
        dna = _VISUAL_DNA.get(project_category, _DEFAULT_DNA)
        return {
            "category": project_category,
            "must_do": dna["must_do"],
            "must_not_do": dna["must_not_do"],
        }

    def generate_research_report(self, project_category: str) -> Dict:
        refs = self.get_research_references(project_category)
        dna = self.generate_visual_dna(project_category)
        return {
            "category": project_category,
            "visual_brief": (
                "Study real product patterns from the references below. "
                "No pre-made colors or fonts are supplied — derive tokens from approved brand direction only."
            ),
            "top_3_products": refs["top_3_products"],
            "top_3_inspo_sites": refs["top_3_inspo_sites"],
            "do_this": dna["must_do"],
            "not_this": dna["must_not_do"],
            "token_policy": refs["token_policy"],
        }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate token-free visual research")
    parser.add_argument("--category", default="Generic Professional")
    args = parser.parse_args()
    print(json.dumps(VisualResearchEngine().generate_research_report(args.category), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
