# R37 — narrative interaction redesign: Cinematic single-stage pilot

## The screenshot exposed a structural bug, not merely a palette issue
User-provided screenshot shows:
1. A large external section heading and a separate embedded HTML component heading visible simultaneously ("DESCEND INTO THE STORY" repeated).
2. The object in the embedded demo is unrelated to the landscape, so the viewer gets two concurrent visual narratives.
3. A cropped persistent "CHAPTERS" floating control overlays the composition.
4. The page has a full-screen background but does NOT yet have a single focus, shared scene, or scroll-directed shot sequence.

## Open-source research and what was actually reused
- [GSAP official scrolltrigger skill](https://github.com/greensock/gsap-skills/blob/main/skills/gsap-scrolltrigger/SKILL.md) — MIT skill/guidance for pinned scenes, scrubbed timeline and transform-first motion.
- [Codrops SeamTransitions](https://github.com/codrops/SeamTransitions) — MIT examples of edge/scene transitions using GSAP, WebGL and canvas.
- [Codrops ScrollBasedLayoutAnimations](https://github.com/codrops/ScrollBasedLayoutAnimations) — MIT scroll-based layout changes using GSAP ScrollTrigger and Flip.
- [Lenis](https://github.com/darkroomengineering/lenis) — MIT smooth scrolling; reviewed but NOT installed because Motion Studio currently includes nested, sandboxed iframes and an existing R16 scroll loop. Adding a second independent loop would be an unnecessary regression risk.

The R37 prototype **adapts design principles** and writes its own integration code; it does NOT claim Codrops/GSAP/Lenis library code was installed or copied. Material GitHub license/reuse should be reviewed if vendor imports happen later.

## R37 integration
- `stage9/r37-story-director.mjs`: embeds an opt-in Cinematic shot director through the established export pipeline. Only Cinematic pages are wrapped in `r37-scene > r37-stage`, with sticky full-viewport visual stage and a deliberate longer scroll corridor.
- One photographic layer and one section heading are visibly authoritative. The unrelated embedded micro-demo iframe remains in the document for edit/restore, but is hidden and unfocusable on the exported cinematic page. This is a deliberate first-iteration restriction: preserving the scene content while avoiding an unrelated second interaction is preferable to showing clashing narratives.
- Scroll motion reuses R16's `--r16-photo-x`, `--r16-photo-y`, and `--r16-incoming`. R37 does NOT add any new scroll or RAF timer; subtle pointer depth changes do not alter the R16 chapter timeline.
- The compact R36 chapter-navigation label is now fully hidden in collapsed mode rather than being cropped. All chapter buttons still exist and are accessible when expanded.
- Product 3D keeps its real 3D panel in this iteration. Unlike Cinematic, it has NOT been converted to a single-subject, unified 3D-material interaction. That needs separate creative direction/assets.
- The original 33 collage source images remain untouched; this is not production art signoff.

## Automated acceptance
- R37 Node source contract: syntax, one exported director, template scoping, no second scroll loop.
- R36+R37 real Chromium pilot: scene/nav structure, desktop/mobile responsiveness and exported HTML.
- `stage9/tests/test_r37_story_director.py` additionally measures true browser sticky hold across two scroll positions and ensures the unrelated iframe does not appear.
- `stage9/tests/test_r14_chapter_navigation.py` validates intentionally collapsed chapter drawer rather than asserting obsolete always-visible nav buttons.
- `stage9/tests/test_product_restructure.py` validates cinematic single-image story rather than requiring an unrelated second iframe to remain visibly rendered.

## User comparison
Live evaluation environment (only after its deployment workflow PASS):
https://mrs-zhong1.github.io/motion-studio-web/r18-ai-review/

The independent R37 concept prototype (two genuine user-approved R29 source photographs) was created during the conversation and passed actual desktop + mobile Chromium scroll, menu and overflow checks. It is NOT the same as the integrated 5-chapter template and cannot be used as production browser evidence.

## Status & next decision
R37 is a **visual trial**, not an approved production design. The next user decision must assess whether the single-stage sticky Cinematic direction is closer to the reference. If not, investigate image shot sequencing, advanced WebGL masked transitions, or actual product-coupled 3D stages using GSAP timelines and Codrops ideas. Only after this acceptance should source-art generation for all 8 templates resume.
