"""
infer_animations.py â€” Recommends animation strategy and generates CSS keyframes.
Outputs: .ui-bridge/animations.json
"""
import json
import sys
import argparse
from pathlib import Path

from infer_engine import ProjectTypeInferrer, collect_text_lines


class AnimationRecommender:

    ANIMATION_PROFILES = {
        'EdTech': {
            'personality': 'encouraging and smooth',
            'duration_base': '300ms', 'duration_fast': '150ms', 'duration_slow': '500ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-2px)', 'hover_shadow': '0 8px 25px rgba(0,0,0,0.12)',
            'page_transition': 'fade-slide-up', 'card_entrance': 'fade-in-up',
            'scroll_reveal': True, 'skeleton_loading': True, 'progress_bars': True,
            'forbidden': ['bounce', 'elastic', 'spin-forever', 'flash'],
        },
        'SaaS Dashboard': {
            'personality': 'precise and efficient',
            'duration_base': '150ms', 'duration_fast': '100ms', 'duration_slow': '300ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-1px)', 'hover_shadow': '0 4px 12px rgba(0,0,0,0.08)',
            'page_transition': 'fade', 'card_entrance': 'fade-in',
            'scroll_reveal': False, 'skeleton_loading': True, 'number_counting': True,
            'forbidden': ['bounce', 'elastic', 'dramatic-slide', 'spin-forever'],
        },
        'E-commerce': {
            'personality': 'snappy and satisfying',
            'duration_base': '200ms', 'duration_fast': '150ms', 'duration_slow': '400ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-4px)', 'hover_shadow': '0 12px 30px rgba(0,0,0,0.15)',
            'page_transition': 'fade-slide', 'card_entrance': 'fade-in-up',
            'add_to_cart': 'scale-pop', 'scroll_reveal': True, 'skeleton_loading': True,
            'forbidden': ['bounce', 'elastic', 'spin-forever'],
        },
        'Booking Platform': {
            'personality': 'calm and trustworthy',
            'duration_base': '250ms', 'duration_fast': '150ms', 'duration_slow': '450ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-2px)', 'hover_shadow': '0 6px 20px rgba(0,0,0,0.1)',
            'page_transition': 'fade-slide-up', 'card_entrance': 'fade-in-up',
            'scroll_reveal': True, 'skeleton_loading': True,
            'forbidden': ['bounce', 'elastic', 'dramatic', 'spin-forever'],
        },
        'Healthcare': {
            'personality': 'gentle and reassuring',
            'duration_base': '300ms', 'duration_fast': '200ms', 'duration_slow': '500ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-1px)', 'hover_shadow': '0 4px 16px rgba(0,0,0,0.08)',
            'page_transition': 'fade', 'card_entrance': 'fade-in',
            'scroll_reveal': False, 'skeleton_loading': True,
            'forbidden': ['bounce', 'elastic', 'dramatic', 'rapid', 'spin-forever'],
        },
        'Fintech': {
            'personality': 'authoritative and stable',
            'duration_base': '200ms', 'duration_fast': '150ms', 'duration_slow': '350ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-1px)', 'hover_shadow': '0 4px 12px rgba(0,0,0,0.1)',
            'page_transition': 'fade', 'card_entrance': 'fade-in',
            'number_counting': True, 'scroll_reveal': False, 'skeleton_loading': True,
            'forbidden': ['bounce', 'elastic', 'dramatic', 'playful', 'spin-forever'],
        },
        'Travel/Hospitality': {
            'personality': 'immersive and aspirational',
            'duration_base': '400ms', 'duration_fast': '200ms', 'duration_slow': '600ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-6px) scale(1.02)',
            'hover_shadow': '0 20px 40px rgba(0,0,0,0.2)',
            'page_transition': 'fade-zoom', 'card_entrance': 'fade-in-up',
            'scroll_reveal': True, 'image_zoom_hover': True,
            'forbidden': ['bounce', 'elastic', 'spin-forever', 'rapid'],
        },
        'Food & Beverage': {
            'personality': 'warm and inviting',
            'duration_base': '300ms', 'duration_fast': '200ms', 'duration_slow': '500ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-4px)', 'hover_shadow': '0 10px 25px rgba(0,0,0,0.12)',
            'page_transition': 'fade-slide-up', 'card_entrance': 'fade-in-up',
            'image_zoom_hover': True, 'scroll_reveal': True,
            'forbidden': ['bounce', 'elastic', 'spin-forever'],
        },
        'Real Estate': {
            'personality': 'premium and sophisticated',
            'duration_base': '350ms', 'duration_fast': '200ms', 'duration_slow': '600ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-4px)', 'hover_shadow': '0 16px 40px rgba(0,0,0,0.12)',
            'page_transition': 'fade', 'card_entrance': 'fade-in-up',
            'image_zoom_hover': True, 'scroll_reveal': True,
            'forbidden': ['bounce', 'elastic', 'rapid', 'playful', 'spin-forever'],
        },
        'Creative Agency': {
            'personality': 'bold and expressive',
            'duration_base': '250ms', 'duration_fast': '150ms', 'duration_slow': '500ms',
            'easing_primary':  'cubic-bezier(0.16, 1, 0.3, 1)',
            'easing_entrance': 'cubic-bezier(0.16, 1, 0.3, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-6px)', 'hover_shadow': '0 20px 40px rgba(0,0,0,0.15)',
            'page_transition': 'slide-diagonal', 'card_entrance': 'fade-in-up',
            'text_reveal': True, 'scroll_reveal': True,
            'forbidden': ['bounce', 'spin-forever', 'blink'],
        },
        'Marketing/CRM': {
            'personality': 'confident and conversion-focused',
            'duration_base': '250ms', 'duration_fast': '150ms', 'duration_slow': '450ms',
            'easing_primary':  'cubic-bezier(0.4, 0, 0.2, 1)',
            'easing_entrance': 'cubic-bezier(0, 0, 0.2, 1)',
            'easing_exit':     'cubic-bezier(0.4, 0, 1, 1)',
            'hover_lift': 'translateY(-3px)', 'hover_shadow': '0 8px 24px rgba(0,0,0,0.12)',
            'page_transition': 'fade-slide-up', 'card_entrance': 'fade-in-up',
            'scroll_reveal': True, 'skeleton_loading': True,
            'forbidden': ['bounce', 'elastic', 'spin-forever'],
        },
    }

    CSS_KEYFRAMES = {
        'fade-in':   '@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }',
        'fade-in-up':'@keyframes fadeInUp { from { opacity:0; transform:translateY(24px); } to { opacity:1; transform:translateY(0); } }',
        'fade-in-down':'@keyframes fadeInDown { from { opacity:0; transform:translateY(-24px); } to { opacity:1; transform:translateY(0); } }',
        'fade-in-left':'@keyframes fadeInLeft { from { opacity:0; transform:translateX(-24px); } to { opacity:1; transform:translateX(0); } }',
        'fade-in-right':'@keyframes fadeInRight { from { opacity:0; transform:translateX(24px); } to { opacity:1; transform:translateX(0); } }',
        'scale-pop': '@keyframes scalePop { 0%{transform:scale(1);} 50%{transform:scale(1.05);} 100%{transform:scale(1);} }',
        'skeleton':  '@keyframes skeleton { 0%{background-position:-200% 0;} 100%{background-position:200% 0;} }',
        'spin':      '@keyframes spin { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }',
        'pulse':     '@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.5;} }',
        'bounce-in': '@keyframes bounceIn { 0%{opacity:0;transform:scale(.3);} 50%{opacity:1;transform:scale(1.05);} 70%{transform:scale(.9);} 100%{transform:scale(1);} }',
    }

    def recommend(self, project_category):
        return self.ANIMATION_PROFILES.get(
            project_category, self.ANIMATION_PROFILES.get('EdTech', {}))

    def generate_css_variables(self, profile):
        return '''\
:root {
  --duration-fast:   %s;
  --duration-base:   %s;
  --duration-slow:   %s;
  --ease-primary:    %s;
  --ease-entrance:   %s;
  --ease-exit:       %s;
}''' % (profile.get('duration_fast', '150ms'),
        profile.get('duration_base', '300ms'),
        profile.get('duration_slow', '500ms'),
        profile.get('easing_primary',  'cubic-bezier(0.4,0,0.2,1)'),
        profile.get('easing_entrance', 'cubic-bezier(0,0,0.2,1)'),
        profile.get('easing_exit',     'cubic-bezier(0.4,0,1,1)'))

    def generate_keyframes(self, profile):
        needed = ['fade-in', 'fade-in-up', 'skeleton', 'spin', 'pulse']
        if profile.get('add_to_cart'):
            needed.append('scale-pop')
        if profile.get('card_entrance') == 'fade-in-up':
            needed.append('fade-in-up')
        return '\n'.join(self.CSS_KEYFRAMES[k] for k in needed if k in self.CSS_KEYFRAMES)

    def generate_utility_classes(self, profile):
        dur  = profile.get('duration_base', '300ms')
        slow = profile.get('duration_slow', '500ms')
        ease = profile.get('easing_primary',  'cubic-bezier(0.4,0,0.2,1)')
        ent  = profile.get('easing_entrance', 'cubic-bezier(0,0,0.2,1)')
        lines = [
            '.animate-fade-in      { animation: fadeIn ' + dur + ' ' + ent + ' both; }',
            '.animate-fade-in-up   { animation: fadeInUp ' + dur + ' ' + ent + ' both; }',
            '.animate-fade-in-down { animation: fadeInDown ' + dur + ' ' + ent + ' both; }',
            '.animate-scale-pop    { animation: scalePop 200ms ' + ease + '; }',
            '.animate-spin         { animation: spin 1s linear infinite; }',
            '.animate-pulse        { animation: pulse 2s ease-in-out infinite; }',
            '.delay-100 { animation-delay:100ms; }',
            '.delay-200 { animation-delay:200ms; }',
            '.delay-300 { animation-delay:300ms; }',
            '.delay-400 { animation-delay:400ms; }',
            '.delay-500 { animation-delay:500ms; }',
            '.skeleton {',
            '  background: linear-gradient(90deg,var(--color-border) 25%,',
            '    var(--color-bg-subtle) 50%,var(--color-border) 75%);',
            '  background-size:200% 100%;',
            '  animation:skeleton 1.5s ease-in-out infinite;',
            '  border-radius:4px;',
            '}',
            '.transition-base { transition:all ' + dur  + ' ' + ease + '; }',
            '.transition-fast { transition:all 150ms ' + ease + '; }',
            '.transition-slow { transition:all ' + slow + ' ' + ease + '; }',
            '@media (prefers-reduced-motion:reduce) {',
            '  *,*::before,*::after {',
            '    animation-duration:.01ms !important;',
            '    animation-iteration-count:1 !important;',
            '    transition-duration:.01ms !important;',
            '  }',
            '}',
        ]
        return '\n'.join(lines)

    def generate_hover_css(self, component_type, profile):
        lift = profile.get('hover_lift', 'translateY(-2px)')
        shadow = profile.get('hover_shadow', '0 8px 25px rgba(0,0,0,0.12)')
        dur = profile.get('duration_base', '300ms')
        ease = profile.get('easing_primary', 'cubic-bezier(0.4,0,0.2,1)')
        return ('.%s { transition:transform %s %s,box-shadow %s %s; }\n'
                '.%s:hover { transform:%s; box-shadow:%s; }'
                % (component_type, dur, ease, dur, ease,
                   component_type, lift, shadow))

    def get_scroll_reveal_js(self, profile):
        if not profile.get('scroll_reveal'):
            return ''
        return '''\
<script>
(function() {
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('[data-reveal]').forEach(function(el) {
    observer.observe(el);
  });
})();
</script>
<style>
[data-reveal] { opacity:0; transform:translateY(24px); transition:opacity .4s ease,transform .4s ease; }
[data-reveal].revealed { opacity:1; transform:none; }
</style>'''


def main():
    parser = argparse.ArgumentParser(description='Infer animation system')
    parser.add_argument('--root', default='.')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    text_lines = collect_text_lines(root)
    category = ProjectTypeInferrer().infer(text_lines).get('category', 'Generic Professional')

    rec = AnimationRecommender()
    profile = rec.recommend(category)

    result = {
        'category':         category,
        'profile':          profile,
        'css_variables':    rec.generate_css_variables(profile),
        'keyframes':        rec.generate_keyframes(profile),
        'utility_classes':  rec.generate_utility_classes(profile),
        'scroll_reveal_js': rec.get_scroll_reveal_js(profile),
    }

    out_dir = root / '.ui-bridge'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'animations.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    if not args.quiet:
        print('Animations: %s profile (%s)' % (profile.get('personality', ''), category),
              file=sys.stderr)
        print('Saved: .ui-bridge/animations.json', file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

