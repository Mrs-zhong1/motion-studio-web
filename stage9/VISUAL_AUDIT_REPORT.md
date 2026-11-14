# Motion Studio — U2 Visual Render Audit

**Date:** 2026-11-14  
**GitHub Actions run:** [43599908353](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43599908353)  
**Outcome:** Chromium PASS · Firefox PASS · WebKit PASS. New desktop/mobile template geometry audit PASS on Chromium.

## Persistent screenshot gallery (new)

The previously ephemeral CI screenshots are now published into the **same review branch**, at [visual-evidence/README.md](visual-evidence/README.md). The full gallery contains **16 actual PNG files**, from 8 templates × desktop/mobile. GitHub Actions run [43600609916](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43600609916) confirmed that image capture, three-browser E2E and the screenshot-persistence step all succeeded.

A separate public static review copy is committed in [motion-studio-web-pages](https://github.com/Mrs-zhong1/motion-studio-web-pages) as `review-preview.html`; its root `index.html` now points to the template gallery. This is a **review build only**, not a production release. The GitHub Pages workflow was added, but external web availability has **not yet been verified**, so the GitHub Pages URL should not be represented as live.

## Scope and evidence
The test `tests/test_template_visual_audit.py` opens the actual built offline editor and preview renderer, captures the first section of each template (desktop 1440×900 and mobile 390×844), and checks **all** chapter photos are present; their CSS background is a data URI; image layer rectangles have nonzero size; chapters have adequate geometric size; and page width does not overflow. Hashes refer to PNG screenshots generated in the CI runner. Because repository Actions artifact storage quota is exhausted, these PNGs were **not uploaded**. Inspect workflow logs/step summary for verified metrics.

| Template | Desktop photos | Mobile photos | Horizontal overflow | Desktop screenshot SHA256 prefix | Mobile SHA256 prefix |
|---|---:|---:|---:|---|---|
| Editorial Portfolio | 4/4 | 4/4 | 0 px | `23133be408c5a867` | `da05b788db0835a3` |
| 3D Product Experience | 4/5 prominently visible | 4/5 prominently visible | 0 px | `5df533591dff4f1e` | `07e89183fa6af054` |
| Cinematic Journey | 5/5 | 5/5 | 0 px | `d89681fef715cc04` | `257698918a222f68` |
| Architecture Studio | 5/5 | 5/5 | 0 px | `3252d42c06d83f6b` | `7f2ffcfed3c1fa7c` |
| Creative Agency | 5/5 | 5/5 | 0 px | `80d29e4ef8decbd6` | `3c26bf5c6677a1f0` |
| Fashion Lookbook | 5/5 | 5/5 | 0 px | `32a60f607f5c1576` | `4e467cc4e53d038b` |
| Interactive Gallery | 5/5 | 5/5 | 0 px | `4c325513fb561e5c` | `400d455ad03d3f9c` |
| Modern SaaS | 5/5 | 5/5 | 0 px | `137938e1552f545f` | `1e4da2e4c6a6311e` |

**3D exception:** A product scene deliberately dims one photo to keep the actual 3D renderer visible; the section still has an embedded photograph. This is explicitly checked rather than silently excluded.

## What the PASS does not prove
- No human reviewed these captured pictures for visual sophistication, typography, art direction or reference-site fidelity.
- Screenshots are generated on the runner but not retained as downloadable artifacts.
- Distinct photographs and rights clearance **have not** been established: offline template chapters may be crops of the same locally bundled JPG.
- Tests ran on headless Playwright browser engines, not native Safari on Apple hardware.
- No production website has been deployed or checked.

## Next acceptance gates
1. Collect legally cleared original media per chapter and maintain provenance.
2. Capture/share reviewable screenshots, complete human visual review against references, then adjust art direction.
3. Validate actual public-hosting URL, preview/editor/export loop and mobile ergonomics before merging into production.
