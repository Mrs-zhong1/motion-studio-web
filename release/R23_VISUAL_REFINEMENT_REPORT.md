# R23 — Eight Template Story Art Direction (2026-11-16)

## Engineering change
- New `stage9/story-art-direction-r23.mjs` adds eight independent art-direction families, chapter variation, typography and image grading.
- `stage9/build-offline.mjs` injects the visual layer after R22 into the exact HTML emitted for offline build and public review. Existing camera, 3D, layer editing, story sequence, data persistence and exports are not rewritten.
- `stage9/tests/test_r23_story_art_direction.mjs` covers template IDs, idempotence guard, timeline preservation, responsive/reduced-motion contract.
- `.github/workflows/r23-story-art-direction.yml` executes contract checks.

## Test evidence
- R23 contract: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43861591511 — PASS.
- R18-R21 review release policy: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43861607607 — PASS.
- Browser E2E on exact new revision: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43861607590 — check status before marking PASS.

## Remaining art-direction release gates — HOLD
1. Capture actual full-story desktop/mobile screenshot pairs per template, inspect legibility, sharpness, crop framing and scene-to-scene visual continuity. CSS-presence tests do not constitute aesthetic approval.
2. Replace or regenerate visibly soft/repetitive images from 33 collage-derived scenes, with source records and commercial terms updated.
3. Human review of hover/scroll/camera motion on all templates; validate real 3D product is not hidden by photo matte.
4. Validate export on latest commit and public preview HTTPS SHA parity; do not merge or publish to production root before visual signoff.

This is a browser-only product. No macOS installation deliverable or native GPU gate is required.
