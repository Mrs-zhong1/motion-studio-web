# R29 — two-scene Cinematic real-image web prototype

Date: 2026-11-16

## What was actually produced
- Two **individually generated images** by OpenAI's in-chat image generator, not Gemini API: (1) panoramic alpine sunset valley, (2) interior train window looking into the same mountain landscape.
- Source native dimensions 1672×941 each. Actual converted JPEGs were separately checked for dimensions and unique SHA-256.
- A self-contained Web HTML prototype and a ZIP with separate JPEGs, story HTML, image evidence, real Chromium screenshots and test report were produced as conversation deliverables; they were **not uploaded to this GitHub repository** and cannot be assumed available at a public GitHub Pages URL.
- Unified scroll-scrub timeline, composited image transition, pointer depth, narrative typography, chapter-navigation dots, progress meter and reduced-motion toggle. One consistent interaction system across two related scenes.
- Desktop Chromium 1440×900 and mobile Chromium 390×844 executed using Playwright against in-memory HTML with data-URI images (local file navigation was blocked by admin policy). Both viewports had 0px horizontal overflow, image2 opacity >0.5 after scroll, progress over 50%, working reduced-motion toggle, navigation, zero uncaught page JS errors.
- Node.js syntax check PASS, but **Firefox/WebKit product E2E and public deployment integrity were NOT tested for this R29 local prototype**.

## Image source metadata
| Scene | Visual | Native | SHA256 of R29 JPEG |
|---|---|---|---|
| 1 | Mountain alpine sunset, fog valleys | 1672×941 | recorded in downloadable r29-assets.json |
| 2 | Rain-streaked train window and mountains | 1672×941 | recorded in downloadable r29-assets.json |

## Repository and production boundary
- Latest release branch Web Product E2E baseline completed PASS at commit `9fdbd500ee4ffe515c3a9b518151771b75a7c203`.
- The R29 downloadable local HTML is a review prototype outside the current build pipeline. No change to 39 stage9/ai-assets source JPEG files has been made in this batch, and the original 33 collage-derived scene files remain.
- Before proposing formal import: review composition and narrative quality; verify provenance/rights, map these two scenes to actual chapter slots, and import to a draft branch using the R25 validated replacement tool. Then run strict AI build, multi-browser product E2E, and full-template screenshots. Human art direction and production deployment remain HOLD.

## Next implementation gate
Import two independently generated sources as an isolated trial inside the template's scene model; compare R29 test HTML against real Cinematic preview/editor/export; use visual screenshots to determine whether chapter titles, section geometry, and camera motion have equivalent quality before repeating for the remaining images.
