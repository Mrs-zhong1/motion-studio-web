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
