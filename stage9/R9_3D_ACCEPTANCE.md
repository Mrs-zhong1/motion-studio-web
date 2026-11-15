# Motion Studio — R9 model + materials + live web delivery (2026-11-15)

Status: **R9-03 / R9-04 / R9-05 engineering milestones implemented; browser CI and live Pages smoke passed.** Do not mistake these for finished visual art direction or native-device GPU performance.

## R9-03 · Original curved headphones GLB
- `builtInHeadphoneGlb()` in `Motion-Studio-Unified-Editor.html` generates an original, independent, reproducible glTF 2.0 GLB at runtime; no unknown-source third-party model was downloaded.
- Replaced five scaled boxes with sampled smooth surfaces: continuous over-ear shells, ear cushions, speaker interiors, metal outer gaskets, curved yokes and padded headband.
- The binary contains indexed positions, normals, four independent PBR material primitives and a valid scene/buffer structure.
- Real Playwright test requires **>=10,000 triangles** loaded in Three.js, **>=4 PBR materials** and successful GLB export. This is a more detailed original demo, **not professionally commissioned product geometry**.

## R9-04 · IBL, texture details and scene controls
- `three-scene-entry.js` bundles `RoomEnvironment`, generates a local PMREM map and assigns it as the scene's image-based lighting environment. No external HDRI download.
- Two deterministic original procedural maps contribute normal and roughness surface variation; these are not hand-authored, high-resolution product textures.
- Four-light studio rig, circular product plinth, soft shadows, ACES/SRGB and the WebGL2 canvas remain in use.
- Users can click **Warm / Cool / Neutral** light presets, **Original / Graphite / Pearl** material choices and **Front / Angle / Detail** view buttons. Pointer-drag orbit, double-click reset and Ctrl/Command+wheel dolly are active.
- R9 status diagnostics expose environmentReady, texture count, modelTriangles, materialCount, lightPreset, materialPreset and cameraPreset. Tests mutate real UI controls and verify changed state, and validate render frames without remote requests.

## R9-05 · Actual web publication
- `build-offline.mjs` compiles the full browser-only editor with both Three.js scene bundles. `prepare-online-preview.mjs` safely stages UTF-8 parts of the generated full HTML and manifest hash under `online-review-parts/`.
- `.github/workflows/prepare-r9-online-review.yml` builds the source package and safely commits its transportable parts. CI verifies their concatenation, byte length, SHA-256 and bundled engine markers.
- The full R9 HTML (**2,336,512 UTF-8 bytes**) was reconstructed without truncation and pushed to `Mrs-zhong1/motion-studio-web-pages/main`, `review-preview.html` commit `52ea2cddddb709b660d81b87ea7f87fd59944f17`. GitHub Pages also serves the root redirect.
- Pages build and deployment [43700485829](https://github.com/Mrs-zhong1/motion-studio-web-pages/actions/runs/43700485829) PASS.
- The stronger live test [43700802307](https://github.com/Mrs-zhong1/motion-studio-web-pages/actions/runs/43700802307) PASS: actual HTTPS Pages fetch, bundled engine markers, opening the Product template from the live site, exporting a real product page, loading its bundled Three.js WebGL2 and verifying environmentReady, >=10,000 triangles and PBR scene behavior.
- URL: https://mrs-zhong1.github.io/motion-studio-web-pages/ (review, **not a production release**).

## Real CI acceptance
- Source browser matrix [43700312213](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43700312213): Chromium PASS, Firefox PASS, WebKit PASS; Chromium includes detailed R9 WebGL2 test and screenshot evidence.
- Live smoke tests use headless Chromium with SwiftShader: success establishes browser/WebGL functionality, **not hardware acceleration, battery consumption, native Safari, or visual quality**.

## Remaining release blockers
1. Human visual evaluation of actual model silhouette, specular response, image composition, animation and controls, compared to professional product pages.
2. Replace remaining provisional photographic assets and clear any commercial redistributable rights if templates are to be sold.
3. Independently test on real Safari/macOS, mobile devices and machines without WebGL2; check fallback and measure frame time/device memory.
4. Provide true product-grade, hand-authored geometry and richer albedo/normal/roughness details if the design needs photorealistic output.
5. Confirm stable hosted deployment through the intended release channel; code remains on draft source PR and has not been merged to production.

This report distinguishes implemented engineering changes and measured tests from design approval.
