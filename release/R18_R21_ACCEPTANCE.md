# R18–R21 Web-only release — revised acceptance

**Product**: browser-based Motion Studio. No native macOS/iOS/Android application; no native phone hardware benchmark gate.

**Current checkpoint**: R17 public review evidence remains the historical baseline. R18–R21 production status is HOLD until demonstrably complete.

## R18 — AI original-first media and visual redesign
- Replace the 39 historical Unsplash-origin chapter photo entries with distinct AI-generated media, matching eight template story arcs (4 editorial, 5 each other template).
- The source manifest MUST list file, source prompt, generation system, generation date, output hash, checked commercial-use terms and any known restrictions for each asset. Do not call third-party photos AI-generated.
- Generate content consistent across chapter openings, middle and endings. Preserve 20 components and full-story scroll/hover/camera preview. Re-run desktop and 390px screenshot comparisons.
- Art direction requires review of actual page results; cover or thumbnail screenshots do not suffice.

## R19 — browser performance, not physical device tests
- Chromium, Firefox, WebKit automated regression at desktop 1440×900 and mobile viewport 390×844.
- Browser-measured scroll animation frame times (median/p95), layout overflow, media decode failures, WebGL availability/fallback, memory where supported and reduced-motion behavior.
- Native phone hardware, thermal throttling or Apple GPU measurements are explicitly **not** release blockers.

## R20 — editing and export contract
- Template discovery → interactive preview → choose template → text/image edits → save → reopen → export → independent exported page.
- Validate data persistence, no broken assets, console errors, offline images and keyboard responsive controls.
- For AI-generated imagery, inspect source provider usage terms and prohibited likeness/branding risks. No old Unsplash per-photo license register once replaced.

## R21 — actual web delivery
- Rebuild exact source revision, run 3-engine browser CI and complete HTTPS artifact SHA-256 match.
- Production gate requires evidence for artDirection, aiAssets, browserPerformance, productFlows, browserRegression, liveIntegrity.
- Deploy only when gate PASS; review URLs remain available during HOLD.

## Code and tests
```sh
python -m unittest discover -s release -p 'test_*.py' -v
python release/check_release.py --mode review --output release-status.json
python release/check_release.py --mode production
```
**Important**: the currently published review build still uses earlier demo photography. Editing this release policy alone does not replace embedded HTML images or imply finished AI media. No secret API keys should appear in manifests.
