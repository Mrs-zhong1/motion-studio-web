# R30 — Cinematic native dual-scene integration (review-only)

Date: 2026-11-16
Branch: `release/r18-r21-acceptance-gates`
Source: `stage9/r30-cinematic-trial.mjs` injected by `stage9/build-offline.mjs`.

## Actual Web product result
The Cinematic Journey template now offers **导入双场景试片** inside template preview and **Cinematic 双场景试片** inside its original editor. It does not create a second stand-alone story renderer. R16 camera/scroll and existing five authored chapter sections remain the only story engine.

User selects two 1600×900+ native 16:9 JPEG/PNG/WebP files at once. Files sorted by filename map to chapters 2 and 3. Import validates BOTH files (native pixel size and decoding, MIME, file length, distinct images) before updating either the template photo cache or current Cinematic project. File size is capped at 1.7 MB per scene to match existing 2.5 MB project image data-URI limit. No existing chapter 1,4,5 or any other template photos are modified.

The same two project images persist through:
1. Cinematic template immersive preview (export `srcdoc`);
2. `Use template` into built-in visual editor;
3. JSON save and reopen;
4. Standalone HTML export.

The image metadata is `user-upload`, `rightsReviewed: false`. Upload does not falsely assert verified AI provenance or clear commercial rights. The official stage9/ai-assets manifest and 33 pending low-resolution scenes are not overwritten.

The renderer/export parity wrapper adds the existing R23 art-direction CSS to the exported HTML and an explicit `data-r30-dual-scene=true` marker when the current project contains both uploaded scenes.

## Verified review deployment
**Review URL:** https://mrs-zhong1.github.io/motion-studio-web/r18-ai-review/

**GitHub Actions:** https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43881460522
Result: PASS — strict 39-file AI build, Chromium trial importer smoke, deploy under `/r18-ai-review/` without production root modification, live HTTPS SHA256 verification, live preview/save/export smoke.

**Full browser matrix:** R30 injected build triggers Web Product E2E for Chromium, Firefox and WebKit; verify the latest commit's run status before calling the full matrix PASS. R30-specific browser fixture tests the two-scene import in Chromium with generated 1600×900 PNG test images; these synthetic test fixtures are NOT visual assets.

## How to test with R29 source files
1. Visit the review URL. From the gallery, open Cinematic Journey template.
2. Choose `导入双场景试片` and select **both** `r29-cinematic-scene-01.jpg` and `r29-cinematic-scene-02.jpg` from the R29 ZIP.
3. Use the chapter filmstrip to inspect scenes 2 and 3, and scroll the live preview; click `使用这个模板`.
4. Edit chapter labels/camera/layers, then `保存 JSON` and `导出 HTML`. Reopening the saved JSON should retain images; the exported HTML should work without any image CDN.
5. Compare 1440×900 desktop and 390×844 mobile. This is an interactive trial and does not imply reference-grade art direction.

## Known limitations and holds
- R29 image files are **not committed into the repository** in R30; the user selects the genuine two trial images in the browser. The public review page initially retains its existing AI chapter images.
- R30 composes the two imported images using the real existing R16 chapter-seam narrative, not the exact 420vh stand-alone R29 scroll timeline. Further motion judgement is an explicit visual-art gate.
- Asset quality across all 33 remaining collage-derived scenes remains HOLD.
- No production release approval or main site replacement; review-only URL.
