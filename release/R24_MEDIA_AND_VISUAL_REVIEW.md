# Motion Studio R24 — Native image-quality and fresh rendered evidence (2026-11-16)

## Verified baseline
- R23 full-browser E2E PASS: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43861737306
- R24 native quality analysis PASS (script integrity and report generation; **not** image-quality approval): https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43863366239
- Fresh screenshot job: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43863507102 (status must be checked separately; do not infer PASS from this record)
- Source of truth: `stage9/ai-assets/manifest.json` and `stage9/tests/audit_r24_source_quality.py`.

## Findings and release implications
- 39 original or AI-derived scene files represent 8 templates.
- 33 scenes derive from collage crops, not independently generated full-resolution scenes.
- Collage source cuts are reported by the manifest as 828×306 and are presented in 1600×900 layouts; upscaling cannot restore missing native detail.
- Automated audit compares native source dimensions, target dimensions, source provenance, crop aspect-ratio risk and chapter completeness. `--enforce` blocks production while flagged scenes remain.
- The test distinguishes source-resolution risk from perceptual sharpness: do not claim a scene is subjectively blurry solely from its dimensions.
- Existing R17 screenshots are historical and must not be substituted for new R23/R24 screenshots.
- The R24 screenshot workflow rebuilds strict AI-only offline HTML, checks complete chapters in real Chromium and generates fresh desktop/mobile opening, middle, ending and immersive screenshots. Screenshots are uploaded as optional CI artifacts; GitHub artifact quota may still prevent retention.

## What is still not done
1. Replace/individually regenerate collage-derived low-source-resolution scenes; preserve manifest hashes and usage record.
2. Human full-chapter visual approval: image focus, text contrast, editorial sequencing, motion depth, unique template identity.
3. Inspect R24 screenshot gallery when uploaded, fix any failed viewport/scene, rerun all browsers after actual image changes.
4. Do not promote review build or set `artDirection=APPROVED` merely from a green CI run.

Production release remains **HOLD**. This is a Web-only product.
