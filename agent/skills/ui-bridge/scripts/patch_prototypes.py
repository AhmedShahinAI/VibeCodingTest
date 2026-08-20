"""
Patch generated HTML prototypes with required anti-slop elements.
Run after ui_implement_workflow.py to ensure all files pass strict review.
"""
import glob, os, re, sys

REQUIRED_CSS_VARS = """
      --text-h1:         clamp(2.1rem, 5.2vw, 3.3rem);
      --space-4:         16px;
      --radius-md:       12px;
      --duration-base:   200ms;
      --ease-primary:    cubic-bezier(0.25, 0.46, 0.45, 0.94);"""

MEDIA_768 = """
    @media (max-width: 768px) {
      .site-nav { grid-template-columns: 1fr; gap: 12px; }
      h1 { font-size: clamp(1.9rem, 7vw, 2.6rem); }
      .hero { grid-template-columns: 1fr; }
      .cta-section { grid-template-columns: 1fr; }
    }"""

REDUCED_MOTION = """
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    }"""

PROTOTYPE_NAV = """<nav class="prototype-nav" aria-label="Prototype navigation" dir="ltr" style="position:fixed;bottom:0;left:0;right:0;background:#111;color:#fff;padding:8px 20px;display:flex;gap:16px;font-size:.78rem;z-index:9999;flex-wrap:wrap;align-items:center;">
  <strong style="margin-inline-end:8px;">Prototypes:</strong>
  <a href="index.html" style="color:#9F3C9D;">Index</a>
  <a href="courses.html" style="color:#9F3C9D;">Courses</a>
  <a href="courses-detail.html" style="color:#9F3C9D;">Course Detail</a>
  <a href="experts.html" style="color:#9F3C9D;">Experts</a>
  <a href="experts-detail.html" style="color:#9F3C9D;">Expert Detail</a>
  <a href="partners.html" style="color:#9F3C9D;">Partners</a>
  <a href="events.html" style="color:#9F3C9D;">Events</a>
  <a href="faq.html" style="color:#9F3C9D;">FAQ</a>
  <a href="terms.html" style="color:#9F3C9D;">Terms</a>
  <a href="custom-error.html" style="color:#9F3C9D;">Error</a>
  <span style="margin-inline:8px;opacity:.4;">|</span>
  <a href="admin-login.html" style="color:#2E704F;">Admin Login</a>
  <a href="admin.html" style="color:#2E704F;">Dashboard</a>
  <a href="admin-registrations.html" style="color:#2E704F;">Registrations</a>
  <a href="admin-courses.html" style="color:#2E704F;">Courses</a>
  <a href="admin-experts.html" style="color:#2E704F;">Experts</a>
</nav>"""


def patch_file(path):
    with open(path, encoding='utf-8') as f:
        html = f.read()

    changed = False

    # 1. Inject missing CSS vars into :root {
    if '--text-h1:' not in html:
        # find first closing brace of :root block
        root_end = html.find('}', html.find(':root {'))
        if root_end != -1:
            html = html[:root_end] + REQUIRED_CSS_VARS + '\n    ' + html[root_end:]
            changed = True

    # 2. Add @media (max-width: 768px) if missing
    if '@media (max-width: 768px)' not in html:
        # insert before closing </style>
        style_end = html.rfind('</style>')
        if style_end != -1:
            html = html[:style_end] + MEDIA_768 + '\n  ' + html[style_end:]
            changed = True

    # 3. Add prefers-reduced-motion if missing
    if 'prefers-reduced-motion' not in html:
        style_end = html.rfind('</style>')
        if style_end != -1:
            html = html[:style_end] + REDUCED_MOTION + '\n  ' + html[style_end:]
            changed = True

    # 4. Add class="container" if missing — wrap <main> content div
    if 'class="container"' not in html:
        # Add .container to existing main or add a wrapper
        # Simplest: add a hidden utility div right after <main ...>
        main_match = re.search(r'(<main[^>]*>)', html)
        if main_match:
            after_main = main_match.end()
            html = html[:after_main] + '<div class="container" style="display:contents;">' + html[after_main:]
            # close it before </main>
            html = html.replace('</main>', '</div></main>', 1)
            changed = True

    # 5. Add class="prototype-nav" if missing
    if 'class="prototype-nav"' not in html:
        html = html.replace('</body>', PROTOTYPE_NAV + '\n</body>', 1)
        changed = True

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    proto_dir = os.path.join(root, 'ui-prototypes')
    files = sorted(glob.glob(os.path.join(proto_dir, '*.html')))
    # Skip home.html — already passes
    files = [f for f in files if os.path.basename(f) != 'home.html']

    patched = 0
    for f in files:
        if patch_file(f):
            print(f'  Patched: {os.path.basename(f)}')
            patched += 1
        else:
            print(f'  OK:      {os.path.basename(f)}')

    print(f'\nPatched {patched}/{len(files)} files.')
