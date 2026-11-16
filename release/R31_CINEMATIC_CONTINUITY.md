# R31 — Cinematic Shot Continuity and Native R16 Motion Refinement

Date: 2026-11-16. Review branch only.

## Actual code changes
- `stage9/r31-cinematic-continuity.mjs`: cinematic-only finishing rules for photographic scale and contrast, visual handoff, readable typography, mobile image balance, and reduced-motion accessibility.
- These styles consume the **existing R16** `--r16-incoming` scroll progress variable and `r16-story-ready` gate. No competing scroll event listener, second camera engine, independent interaction layout, or additional 3D dependency was added.
- Same CSS is also embedded into the actual exported HTML via an `exportDocument` wrapper, keeping preview/export appearances aligned.
- `stage9/build-offline.mjs`: R31 inserted after R30’s real image import, leaving the existing R23 art direction and R16 camera/scroll logic intact.
- `stage9/tests/test_r31_story_continuity.mjs` validates template scoping, reduced-motion support, idempotence protection, unchanged engine markers and exported parity wrapper.
- `.github/workflows/r31-cinematic-continuity.yml` runs the contract.

## Test evidence
- [R31 visual integration contract: PASS](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43885033742)
- Three-browser Web Product E2E on the new branch: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43885043721 (check result separately; green R31 contract is not a browser pass)
- Strict AI-origin hosted review build on R31 code: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43884966261 (check result before claiming latest live deploy)
- Prior R30 product three-browser acceptance confirmed PASS at commit `64e7b8b7`.

## Known limitations
- R31 fine-tunes photo tone, scale, readability and existing seam variables. It is not a recreation of the stand-alone R29 custom scroll timeline nor a whole-new visual narrative.
- Two genuine R29 source images remain user-selectable in the live trial; R31 code changes do not silently alter official 39 AI images. The 33 collage-derived sources still need independent high-resolution replacement and review.
- A CSS contract cannot prove human-perceived cinematic quality. Manual visual inspection should compare 1440×900 and 390×844 scrolling captures before signing `artDirection` approval.
- Production release is **HOLD**.
