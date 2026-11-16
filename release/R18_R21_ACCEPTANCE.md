# R18–R21 batch acceptance — actual state and handoff

Source branch: `fix/u1-u2-template-first-20261114`, pinned R17 source `e7a90381ab7a421188082f895bbe85b2f5f0c0db`.
This branch adds release verification without disturbing public review or replacing the existing 20 interactive components.
The release process is **fail-closed**. A CI geometry PASS is not approval of art quality, real-device stability, or usage rights.

## R18 — professional visual review / corrections (OPEN)
- Inspect the whole scene sequence, not covers: editorial, product-3d, cinematic, architecture, agency, fashion, gallery, saas; both 1440×900 and 390×844.
- Prioritize Editorial Portfolio and 3D Product Experience against their reference quality: image–type overlap, cinematography, optical hierarchy, connected chapters, hover depth and scroll transitions.
- Compare actual interaction recordings and screenshot evidence against Grande Charte, GSAP Showcase and Motionsites; document observable defects with screenshots, device and source commit.
- Human reviewer signs `artDirection` with evidence URL, name and date only after correction. Automated screenshot hashes are not a proxy.

## R19 — real hardware and 3D (OPEN)
- Test Android Chrome and physical iPhone Safari with model/OS/browser/GPU details, viewport, WebGL availability and repeatable scene path.
- Capture frame-time distribution (median/p95), long frames, memory trend, WebGL context loss, tab background/foreground, reduced-motion and mobile thermal throttling on lengthy scroll interaction.
- Validate PBR lighting, textures, GLB animation, orbit interaction and graceful fallback on real GPUs.
- Do not use desktop WebKit headless runs as evidence of native iPhone Safari performance.

## R20 — commercial quality and source rights (OPEN)
- Exercise actual homepage → 8 previews → use → edit image/text → save → reopen → export → exported page (desktop/mobile).
- Trace all 39 demo photo URLs plus 3D models, brands, people and other media; record owner, license URL, scope, commercial approval, attribution requirements, and release evidence.
- Unsplash-origin image URLs alone do not establish model/property release or transferable rights for every use case.
- Replace unresolved media with owned or specifically licensed content before production. Update source record and per-chapter `commercialRightsApproved` only on independent evidence.

## R21 — final delivery (OPEN)
- Rebuild exact source commit, run Chromium/Firefox/WebKit E2E, capture resulting CI run URLs.
- Verify public HTTPS URL returns 200; compare SHA256 against tested artifact. Record `browserRegression` and `liveIntegrity` separately.
- Merge/release only with R18, R19, R20 approval artifacts AND the production gate result PASS.
- Deliver: working URL, pinned source commit, workflow runs, screenshot/video evidence, rights register, physical device test report, and unresolved issues list.

## How to run
```sh
python -m unittest discover -s release -p 'test_*.py' -v
python release/check_release.py --mode review --output release-status.json
python release/check_release.py --mode production
```
The review command succeeds with HOLD if the R17 automated baseline remains healthy; production exits non-zero while any blocker remains.
Never put credentials or private user information in the approval file.
