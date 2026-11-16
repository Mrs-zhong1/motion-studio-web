# R27 — Real Provider Contract, Cost Safety and Actual Scene Gallery

Date: 2026-11-16. Web-only Motion Studio review branch.

## Corrected production blockers
1. `stage9/generate_r26_ai_scenes.py`: Gemini Interactions request includes `response_format.type=image`, `mime_type=image/png`, `aspect_ratio=16:9`, and `image_size=2K`. Image extraction handles model_output step arrays and documented output_image convenience shape. A generation response must contain a single real encoded image; text-only or incomplete responses fail closed.
2. Request timeout/HTTP 429/5xx are NOT retried automatically: the billable generation may succeed despite a lost response. The operator checks usage before consciously retrying; no silent multiple billable generations.
3. Generated source pixels are not resized to satisfy an arbitrary file limit. The 5MB JPEG serialization constraint is met by stepping compression quality down as necessary without changing source dimensions. Truly oversize files fail.
4. `stage9/review_r27_contact_sheet.py` creates independent visual strips by template from actual validated staging JPEGs and a simple local review HTML. Every image must match source SHA-256, original recorded dimensions and 1600×900 minimum. It never claims art-direction approval.
5. R26 generation Actions workflow generates contact-sheet artifacts on paid generation runs, while the default no-spend run executes R27 regression tests.

## Verified engineering evidence
- R27 dry-run tests (provider payload, output shape, real Pillow image decoding, source-integrity review gallery): **PASS** https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43871357652
- R26 real AI image-generation calls: **NOT RUN** (provider credential and explicit billing authorization not supplied in this project run).
- R27 generated visual comparison gallery for genuine 33 fresh images: **NOT AVAILABLE** until actual R26 generation completes.
- Full Web E2E may run on every code push; check latest workflow status separately.
- No changes to production root or existing 39 committed AI assets.

## Next acceptance
1. Execute a billed image-generation run with GitHub `GEMINI_API_KEY` secret and explicit approval. Start with two paid images to verify actual account compatibility and output quality, then complete remaining 31.
2. Open generated R27 image strips and inspect all narrative sequences (opening/middle/ending); reject images that are thematically incoherent, repetitious, or poor in material quality.
3. Import reviewed full set through R26 draft-PR workflow. Validate exact SHA, images and strict AI HTML, review responsive and scroll story. Confirm full three-browser E2E on imported JPEGs.
4. Approve art direction and production deployment only with real screenshots and visual acceptance; production remains **HOLD**.

Provider documentation (verified Nov 2026):
https://ai.google.dev/gemini-api/docs/image-generation
https://ai.google.dev/gemini-api/docs/interactions-breaking-changes-may-2026

Web-only, no Mac app or DMG.
