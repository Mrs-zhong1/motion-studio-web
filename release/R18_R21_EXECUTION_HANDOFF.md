# Motion Studio Web — R18–R21 delivery record (2026-11-16)

## Product and public review
- Browser-only Web product, eight templates, 20 interactive components.
- **Live isolated R18 AI review:** https://mrs-zhong1.github.io/motion-studio-web/r18-ai-review/
- **Source branch:** `release/r18-r21-acceptance-gates`, draft PR #2.
- The review does **not** replace the existing production root or imply professional art-direction approval.

## Verified engineering delivery
- All 39 original AI-derived JPEG chapter files and `stage9/ai-assets/manifest.json` now **exist in the GitHub repository** (previous missing-assets blocker fixed).
- `MOTION_REQUIRE_AI_ASSETS=1` build is strict: cannot fall back to Unsplash, refuses missing/wrong hash files, embeds all 39 chapters and eight AI preview covers.
- Original source allocation: six stand-alone generated images and 33 crops from AI collage generations, adapted to 1600×900. The 33 adapted scenes have **not** gained native source detail from resampling. Do not call them 33 individually generated full-resolution photographs.
- `stage9/ai-assets/manifest.json` records source, 39 SHA256 hashes, commercial-use terms flags and image presentation metadata.
- `stage9/tests/test_r18_ai_folder_import.py` tests the browser folder import and corruption rollback.
- R19 Stage9 strict WebGL / Meshopt / PBR / 20-components regression: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43812402815 (PASS).
- Latest source integrated 3-engine product E2E: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43817157227 (PASS).
- Review build and public site SHA256: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43819113666 (PASS).
- R21 public review editor login-free Chromium smoke (8 template assets/39 chapters, save JSON, export HTML, no page errors): https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43819473799 (PASS).
- Release policy tests: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43819480325 (PASS).

## Remaining final commercial release criteria
1. **Visual/art-direction gate stays HOLD.** Inspect the actual full-story motion, type hierarchy, image sharpness, contrast and diversity. Rework cropped chapters that look soft or repetitive. Do not infer high-end creative quality from hash or browser CI.
2. Draft PR is deliberately unmerged and main release URL untouched. The source current production gate must return PASS only after independently checking visual quality and any open defects.
3. Once approval is recorded, run production release workflow against exact tested source and verify its deployed HTTPS SHA256 and user-facing editor functions; do not silently overwrite the review or production root beforehand.

## Exactly how to test
1. Open https://mrs-zhong1.github.io/motion-studio-web/r18-ai-review/
2. Choose each of the eight template covers, preview the scroll interactions, click Use.
3. Edit text/images, Save JSON, re-import JSON, Export HTML, open exported page.
4. For audit proofs inspect the GitHub Actions logs and `release/R18_R21_APPROVALS.json`.

No native smartphone hardware/GPU check or old Unsplash third-party license gate is required.


## 2026-11-19 — post-fix engineering revalidation

The following runs were completed against source commit `6afaf1a55288fe997d888d1ec50d5d09df2e53fd` on `release/r18-r21-acceptance-gates`. These are engineering revalidation records, not commercial release signoffs.

### Three.js / offline editor
- Stage 9–15 workflow: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/44435894713 — job `build-and-test` completed successfully.
- Passed checks include offline Three.js bundle/license/no-remote-import verification; deterministic skinned GLB; PBR texture/pixel verification under SwiftShader; GLB compatibility/mobile/offline/performance matrix; invalid-GLB rejection; shared scene/camera across chapters; Stage 10 keyframe JSON roundtrip; Stage 11 spline and draggable keyframes; Stage 12 spline tangent and actual spatial gizmo drag/axis constraints; Stage 13 independent Bezier handles and actual 3D tangent drag/persistence/export; Stage 14 large GLB/compression rejection/undo-redo/shared-renderer stability; and Stage 15 Meshopt encoder/decoder plus single/shared WebGL verification.
- The Stage 9–15 workflow's generated-HTML/evidence commit and production-gate steps were skipped by workflow conditions. Do not interpret the workflow success as a production deployment or a production gate pass.

### Browser E2E
- Cross-browser workflow: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/44435900814 — Chromium, Firefox and WebKit jobs all completed successfully.
- Chromium ran the extended suite: real edit/save/reopen/export; R30; R33; R9; R11; R13; R14; R15 and asset replacement/coverage; R18 provenance/folder import; R19 browser pacing/mobile geometry; R16 transitions/camera/chapter bridges; R17 eight-template storyboards and 390px layout; U1–U4; full eight-template desktop/mobile audit; measurable R17 quality gate; and product discovery/preview/editor journey.
- Firefox and WebKit ran the shared baseline: browser install, edit-save-reopen-export smoke, and template discovery/preview/editor journey. Chromium-only specialist tests were skipped on these engines by the workflow matrix. This is not full specialist parity across all three engines.
- The current workflow's screenshot persistence step was skipped because its condition targets a different branch/event. No new visual screenshot gallery was committed by this run.

### Release gate result
- Release acceptance workflow: https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/44435900807 — automation completed successfully, report result remains **HOLD**, with no automated failures.
- Exact outstanding holds: R18 full-flow visual design review; R21 production HTTPS deployment and tested artifact hash; R25 native-source quality and independent-generation requirements.
- `productionEligible=false`; `nativeSourceQualityEligible=false`. Do not change approval statuses or production root to bypass these holds.

### R25 exact asset remediation inventory
Manifest currently records 39 chapters: 6 stand-alone individual images and 33 collage-derived crops. All 33 crop slots below currently have approximately 828×305/306 native source crops displayed at 1600×900; they fail the independent-generation and native-resolution requirements. The replacement must be a genuinely separate, high-resolution source image for each chapter, not an enlarged crop or metadata-only relabel.

| Template | Chapter slots requiring new individual sources |
|---|---|
| agency | 1, 2, 3, 4, 5 |
| architecture | 2, 3, 4, 5 |
| cinematic | 2, 3, 4, 5 |
| editorial | 2, 3, 4 |
| fashion | 2, 3, 4, 5 |
| gallery | 2, 3, 4, 5 |
| product-3d | 2, 3, 4, 5 |
| saas | 1, 2, 3, 4, 5 |

Each replacement must satisfy all of the following before it can count toward R25:
1. A distinct image file generated as an individual scene (not a crop from a multi-panel collage).
2. Native source dimensions at least 1280×720; for 1600×900 presentation, each upscale ratio must be no more than 1.25.
3. Manifest source type `individual-generation`, `trueHighResolutionGenerated: true`, correct source reference and generation provenance.
4. Recomputed SHA-256 matching the committed image bytes; retain the AI-origin and commercial-use terms record.
5. Re-run `node stage9/test_ai_chapter_assets.mjs`, the Chromium visual/E2E checks, and `python release/check_release.py --mode review`.

The existing six individual images are not included in the 33-slot replacement list. The remaining visual art-direction review must still inspect the full scroll story after replacement. Browser CI success does not provide human art-direction approval.
