"""
infer_master.py â€” Master orchestrator.
Runs all inference modules and writes .ui-bridge/design-system.json + design-system.css
"""
import json
import sys
import argparse
from pathlib import Path
from ui_bridge_core import ApprovalStore, VersionedArtifacts, read_json

# Core engine
from infer_engine import (
    ProjectTypeInferrer, LanguageInferrer, BrandColorInferrer, FontInferrer,
    PageInventoryInferrer, SpecKitArtifactInferrer,
    collect_text_lines, collect_file_contents,
)

# Sub-modules
from infer_typography   import TypographyRecommender
from infer_colors       import ColorSystemBuilder
from infer_images       import ImageStrategyRecommender
from infer_icons        import IconSystemRecommender
from infer_animations   import AnimationRecommender
from infer_layout       import LayoutRecommender
from infer_components   import ComponentLibraryBuilder
from infer_quality      import (
    TypeHierarchyEngine, ColorCombinationEngine, HeroVariationEngine,
    SectionVariationEngine, AntiSlopEnforcer, ImageIntegrationHelper,
    run_quality_checks,
)
from visual_research    import VisualResearchEngine

EXTENSIONS = {'.css', '.scss', '.vue', '.jsx', '.tsx', '.html', '.ts', '.js', '.json', '.md'}


def _safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        print('[WARN] %s: %s' % (fn.__name__ if hasattr(fn, '__name__') else '?', e), file=sys.stderr)
        return {}


def build_design_system(root_path, quiet=False):
    root = Path(root_path).resolve()
    out_dir = root / '.ui-bridge'
    out_dir.mkdir(exist_ok=True)

    approvals = ApprovalStore(root)
    missing_approvals = approvals.require(['brand_direction', 'moodboard', 'visual_layout_dna'])
    if missing_approvals:
        raise RuntimeError(
            'Approval gate failed before design-system generation. Missing: %s.'
            % ', '.join(missing_approvals)
        )
    latest = read_json(out_dir / 'latest.json', default={}) or {}
    intake_name = latest.get('brand-intake')
    intake = read_json(out_dir / intake_name, default={}) if intake_name else {}
    approved_direction = intake.get('approved_direction', {})
    if not approved_direction:
        raise RuntimeError('Approved brand artifact missing approved_direction.')

    def latest_data(name):
        filename = latest.get(name)
        if not filename:
            return {}
        return read_json(out_dir / filename, default={}) or {}

    direction_artifacts = {
        'competitive_analysis': latest_data('competitive-analysis'),
        'moodboard': latest_data('moodboard'),
        'visual_dna': latest_data('visual-dna'),
        'layout_dna': latest_data('layout-dna'),
        'photography_system': latest_data('photography-system'),
        'iconography_system': latest_data('iconography-system'),
        'hero_diversity': latest_data('hero-diversity'),
        'component_personality': latest_data('component-personality'),
        'content_realism': latest_data('content-realism'),
        'narrative_patterns': latest_data('narrative-patterns'),
        'section_diversity': latest_data('section-diversity'),
    }
    missing_artifacts = [name for name, data in direction_artifacts.items() if not data]
    if missing_artifacts:
        raise RuntimeError(
            'Missing direction artifacts before design-system generation: %s.'
            % ', '.join(missing_artifacts)
        )

    if not quiet:
        print('Running master inference on: %s' % root, file=sys.stderr)

    # --- Layer 0: raw data collection ---
    text_lines   = collect_text_lines(root)
    file_content = collect_file_contents(root, EXTENSIONS)

    # --- Layer 1: project type + language ---
    pt    = ProjectTypeInferrer().infer(text_lines)
    lang  = LanguageInferrer().infer(text_lines)

    category  = pt['category']
    is_arabic = lang['is_arabic']
    effective_category = 'EdTech_Arabic' if (is_arabic and category == 'EdTech') else category

    if not quiet:
        print('Category: %s | Arabic: %s' % (category, is_arabic), file=sys.stderr)

    # --- Layer 2: brand discovery ---
    raw_colors = BrandColorInferrer().infer(file_content)
    raw_fonts  = FontInferrer().infer(file_content)

    # --- Layer 4: spec kit ---
    spec = SpecKitArtifactInferrer().infer(root)

    # --- Layer 5: page inventory ---
    page_data = PageInventoryInferrer().infer(text_lines)
    pages     = page_data.get('pages', [])

    if not quiet:
        print('Pages found: %d' % len(pages), file=sys.stderr)

    # --- Layer 6: typography ---
    typo_rec  = TypographyRecommender()
    approved_fonts = approved_direction.get('fonts', {})
    font_pair = {
        'heading': approved_fonts.get('arabic_heading') or approved_fonts.get('heading') or 'Approved Heading Font',
        'body': approved_fonts.get('arabic_body') or approved_fonts.get('body') or 'Approved Body Font',
        'mono': approved_fonts.get('mono') or 'JetBrains Mono',
        'rationale': 'Approved brand direction',
        'google_url': '',
    }
    typo_css  = typo_rec.generate_css_variables(font_pair)
    typo_import = typo_rec.generate_google_fonts_import(font_pair) if font_pair.get('google_url') else ''

    # --- Layer 7: colors ---
    color_builder = ColorSystemBuilder()
    approved_palette = approved_direction.get('palette', {})
    if not all([approved_palette.get('primary'), approved_palette.get('accent'), approved_palette.get('background'), approved_palette.get('surface'), approved_palette.get('text')]):
        raise RuntimeError('Approved brand palette is incomplete.')
    palette = color_builder.generate_full_palette(category, {
        'colors': [
            {'role': 'primary', 'confidence': 'high', 'value': approved_palette.get('primary')},
            {'role': 'accent', 'confidence': 'high', 'value': approved_palette.get('accent')},
        ]
    })
    palette['bg'] = approved_palette.get('background')
    palette['surface'] = approved_palette.get('surface')
    palette['text_primary'] = approved_palette.get('text')
    palette['text_inverse'] = approved_palette.get('text_inverse') or '#FFFFFF'
    color_css     = color_builder.generate_css_output(palette)

    # --- Layer 8: images ---
    img_rec    = ImageStrategyRecommender()
    img_strategy = img_rec.recommend(category)

    # --- Layer 9: icons ---
    icon_rec = IconSystemRecommender()
    icon_data = icon_rec.recommend(category)
    icon_css  = icon_rec.generate_icon_css()

    # --- Layer 10: animations ---
    anim_rec  = AnimationRecommender()
    anim_profile = anim_rec.recommend(category)
    anim_vars = anim_rec.generate_css_variables(anim_profile)
    anim_kf   = anim_rec.generate_keyframes(anim_profile)
    anim_util = anim_rec.generate_utility_classes(anim_profile)

    # --- Layer 11: layout ---
    layout_rec = LayoutRecommender()
    header_pat = layout_rec.recommend_header(category, is_arabic)
    footer_pat = layout_rec.recommend_footer(category, is_arabic)

    # --- Layer 12: components ---
    comp_builder = ComponentLibraryBuilder()
    components   = comp_builder.build_all_components(category, {'palette': palette}, font_pair, is_arabic)

    # --- Layer 13: quality / diversity ---
    quality = run_quality_checks({'category': category, 'is_arabic': is_arabic}, pages)

    # --- Layer 14: visual research ---
    vr_engine     = VisualResearchEngine()
    vr_report     = vr_engine.generate_research_report(category)
    vr_json_path  = out_dir / 'visual-research.json'
    vr_json_path.write_text(
        __import__('json').dumps(vr_report, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    if not quiet:
        print('Written: .ui-bridge/visual-research.json', file=sys.stderr)

    # --- DIVERSITY RULE: 5+ pages must not share the same hero pattern ---
    if len(pages) >= 5:
        hero_ids  = [v['hero_pattern'] for v in quality['hero_assignments'].values()]
        unique_ids = set(hero_ids)
        if len(unique_ids) < min(5, len(hero_ids)):
            print('[WARN] Diversity rule: some pages share the same hero pattern â€” '
                  'hero engine should assign unique patterns for 5+ pages.', file=sys.stderr)

    # --- Assemble design system ---
    design_system = {
        'generated_by':  'infer_master.py',
        'version':       '1.0',
        'root':          str(root),
        'category':      category,
        'effective_category': effective_category,
        'is_arabic':     is_arabic,
        'is_rtl':        lang.get('is_rtl', is_arabic),
        'spec': {
            'project_name': spec.get('project_name', ''),
            'plan_path':    str(spec.get('plan_path', '')),
            'tasks_path':   str(spec.get('tasks_path', '')),
            'phases':       spec.get('phases', 0),
        },
        'pages': pages,
        'typography': {
            'font_pair':    font_pair,
            'css_import':   typo_import,
            'css_variables': typo_css,
        },
        'colors': {
            'palette':      palette,
            'css_variables': color_css,
        },
        'approved_brand': approved_direction,
        'direction_artifacts': direction_artifacts,
        'images': {
            'strategy':     img_strategy,
            'css_helpers':  ImageStrategyRecommender.CSS_IMAGE_HELPERS,
        },
        'icons': {
            'recommended_set': icon_data,
            'css':             icon_css,
        },
        'animations': {
            'profile':       anim_profile,
            'css_variables': anim_vars,
            'keyframes':     anim_kf,
            'utility_css':   anim_util,
        },
        'layout': {
            'header': header_pat,
            'footer': footer_pat,
            'page_structures': layout_rec.PAGE_STRUCTURE_STANDARDS,
        },
        'quality': {
            'type_tier':           quality['type_tier'],
            'type_css':            quality['type_css'],
            'gradients':           quality['gradients'],
            'hero_assignments':    quality['hero_assignments'],
            'section_assignments': quality['section_assignments'],
        },
        'visual_research': {
            'visual_brief':     vr_report['visual_brief'],
            'top_3_products':   vr_report['top_3_products'],
            'top_3_inspo_sites': vr_report['top_3_inspo_sites'],
            'do_this':          vr_report['do_this'],
            'not_this':         vr_report['not_this'],
        },
        'raw_signals': {
            'detected_colors': raw_colors.get('colors', []),
            'detected_fonts':  raw_fonts.get('fonts', []),
            'preset_applied':  None,
        },
    }

    store = VersionedArtifacts(root)
    versioned_design_system = store.write_new('design-system', design_system)

    # --- Write JSON ---
    json_path = out_dir / 'design-system.json'
    json_path.write_text(json.dumps(design_system, ensure_ascii=False, indent=2), encoding='utf-8')

    # --- Assemble CSS ---
    css_parts = [
        '/* ===================================================',
        '   Design System â€” generated by infer_master.py',
        '   Category: %s | Arabic: %s' % (category, is_arabic),
        '=================================================== */',
        '',
        typo_import,
        '',
        '/* === Color Tokens === */',
        color_css,
        '',
        '/* === Typography Tokens === */',
        typo_css,
        '',
        '/* === Type Hierarchy (anti-slop) === */',
        quality['type_css'],
        '',
        '/* === Animation Tokens === */',
        anim_vars,
        '',
        '/* === Animation Keyframes === */',
        anim_kf,
        '',
        '/* === Utility Classes === */',
        anim_util,
        '',
        '/* === Icon Styles === */',
        icon_css,
        '',
        '/* === Image Helpers === */',
        ImageStrategyRecommender.CSS_IMAGE_HELPERS,
        '',
        '/* === Base Reset === */',
        '*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }',
        'html { font-family: var(--font-body, sans-serif); font-size: 16px; }',
        'body { color: var(--color-text-primary); background: var(--color-bg); '
        'line-height: var(--type-body-leading, 1.6); }',
        'img { max-width: 100%; display: block; }',
        'a { color: inherit; }',
        '',
        '/* === Arabic RTL Support === */' if is_arabic else '',
        '[dir="rtl"] { text-align: right; }' if is_arabic else '',
        '[dir="rtl"] .flex-row-reverse-rtl { flex-direction: row-reverse; }' if is_arabic else '',
    ]

    css_output = '\n'.join(p for p in css_parts if p is not None)
    css_path = out_dir / 'design-system.css'
    css_path.write_text(css_output, encoding='utf-8')

    if not quiet:
        print('Written: .ui-bridge/design-system.json', file=sys.stderr)
        print('Written: %s' % versioned_design_system, file=sys.stderr)
        print('Written: .ui-bridge/design-system.css', file=sys.stderr)

    return design_system


def main():
    parser = argparse.ArgumentParser(description='Master design system inference engine')
    parser.add_argument('--root',   default='.')
    parser.add_argument('--quiet',  action='store_true')
    parser.add_argument('--show',   default='',
                        help='Comma-separated keys to print from design-system.json '
                             '(e.g. hero_assignments,type_tier)')
    args = parser.parse_args()

    ds = build_design_system(args.root, quiet=args.quiet)

    if args.show:
        keys = [k.strip() for k in args.show.split(',')]
        partial = {}
        for key in keys:
            for section in ds.values():
                if isinstance(section, dict) and key in section:
                    partial[key] = section[key]
                    break
            else:
                if key in ds:
                    partial[key] = ds[key]
        print(json.dumps(partial, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(ds, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

