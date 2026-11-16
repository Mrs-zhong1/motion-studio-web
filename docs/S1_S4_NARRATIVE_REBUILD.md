# Motion Studio — S1–S4 Narrative Rebuild Contract

**Revision:** 2026-11-16. **Scope:** Eight integrated interactive templates, 20 existing components, single-file offline HTML export and JSON editing. **No framework migration.**

## Root cause corrected in S1

Former Editorial chapters used `buildSection()` to render an independent iframe-based demonstration (including unrelated lime-green posters) over an unrelated AI background photo. R15/R16 effects then tried to cover the seam with masks, yielding a visual collage rather than one story.

The S1 flagship preview instead renders four editorial images and associated text in **one persistent visual stage**. A single normalized scroll position changes image visibility, camera zoom, pointer displacement and typography; reverse scrolling follows the same timeline. R14 retains message-based progress events but its independent floating chapter rail is hidden for this template to avoid double navigation. Existing components remain in `registry` and are still available in the editor.

**Important:** This is a first implemented continuity mechanism, NOT yet a physically simulated fabric shader, complex camera choreography or a faithful clone of Pear / Grande Charte.

## Story contracts per template (S3 scope)

| Template | Central visual object | Continuity & transition contract | Interaction | Status |
|---|---|---|---|---|
| Editorial Portfolio | One cloth/material family and four art-directed scenes | fixed stage, crossfade/zoom, matched typography, reversed scroll | mouse depth | **S1 implemented, art quality pending** |
| 3D Product Experience | One real GLB object for the five chapters | fixed overlay WebGL2/Three.js, continuous scroll camera, model orientation and optional source animation | scroll | **S4 runtime implemented; real browser acceptance pending** |
| Cinematic Journey | Same landscape/time sequence | persistent stage, letterbox masking, filmic scroll zoom | scroll | **S3 first implementation; final art pending** |
| Architecture Studio | Architecture photography sequence | persistent stage, side-geometry wipe, lower-third typography | scroll | **S3 2D first implementation; 3D camera path pending** |
| Creative Agency | One graphic visual language | clipped shape transition and oversized type, no per-chapter iframe | pointer parallax | **S3 first implementation; morph pending** |
| Fashion Editorial | Textile and silhouette photos | ellipse wipe, large fashion typography and material zoom | pointer parallax | **S3 first implementation; material shader pending** |
| Gallery Exhibition | Curated collection in spatial context | circular aperture reveal over fixed stage | story navigation | **S3 first implementation; spatial scene pending** |
| SaaS Product Story | Visual sequence and overlay panel | inset-masked scene changes, persistent UI progress panel | scroll | **S3 first implementation; real stateful demo pending** |

## Shared data contract

One `project.sections` array remains the saved source of truth. `templateId` selects the available renderer. No schema-breaking migration. For each narrative: asset identity, title/copy, camera/effect keyframes, start/end exposure and interactions should be editable. Nonstory user projects and component demos must keep current behavior.

## Reference policy

- **User's seven GitHub repositories** are registered in `open-source-library.json`: shadcn/ui, Creative Tim UI, Nuxt UI, Coss UI, Ant Design, Svelte, Tailwind CSS.
- The implementation takes original UI semantics, accessibility and layout-token design patterns; **no third-party React/Vue/Svelte code is bundled by registration alone**.
- Any future copied source requires exact license/attribution review, framework compatibility evidence and offline build testing.
- Additional earlier sources (Codrops, Barba, Three.js/WebGL, infinite canvas) are research references and will be listed by exact URL only after validation.

## Acceptance gates

1. Editorial preview includes exactly ONE continuous stage with four nonfallback photo chapters, no per-chapter iframe/demo poster, and no duplicate visible navigation.
2. Bidirectional scroll visibly changes scene/state; reduced-motion keeps readable, accessible content; desktop/mobile no horizontal overflow.
3. Text/image edits saved in project JSON must appear in the exported self-contained HTML; other seven templates maintain legacy regression while S3 is incomplete.
4. Chromium, Firefox, WebKit E2E, Stage9 GLB/PBR, and live HTTPS review commit/hash are required for a review release.
5. Full artistic acceptance is separate from CI and will not be marked PASS based on image hashes or template count.

## 2026-11-16 resumed execution update

S3 first implementation now exports **seven** (Editorial + six genres) on one persistent 2D narrative stage. Genre-specific scrubbed masks/camera displacement replace unrelated embedded component demonstrations. Editorial uses 4 chapters; other genres use 5 or any edited chapter count ≥2. The original 20-component editor remains available and the GLB product template is deliberately kept on the existing real Three.js path.

S4 adds a **current-project immersive preview** from the editor's '交互预览' control. It renders `exportDocument()` from the actual edited JSON project, not a newly instantiated original template, and restores control state on return. The new S3/S4 browser tests cover scroll reversal, mask changes, desktop/mobile, reduced-motion, edited text, chapter navigation and export.

**Still not equivalent to Pear.no or Grande Charte:** no physical fabric simulation, sophisticated continuous 3D camera choreography, independent high-resolution AI chapters for the 33 collage-derived crops or art-director sign-off. These remain open; production review cannot claim final completion.

**Testing:** latest full GitHub Actions results must be checked per commit. A passing older S1 commit is not proof of the S3/S4 branch. The live review stays in `/s1-story-review/` and production root remains unchanged.

## Product Story WebGL2 implementation (2026-11-16)

- Added `stage9/product-persistent-story.js`, bundled by `stage9/build-offline.mjs` into a separate **offline data URL** (no public CDN).
- Only `product-3d` with a valid GLB and >=2 sections activates the single-model shared story; others keep existing renderer paths.
- The original model remains in one real Three.js scene across five chapter camera states, interpolated by scroll position. No per-chapter duplicate GLB loading by the new product renderer.
- Existing standalone GLB and previously proven two-model shared Three.js engine are **not removed**, preserving backwards compatibility.
- Browser diagnostic object: `window.__motionProductStory` exposes model load, mesh count, single canvas count, scroll samples and errors.
- New acceptance: `stage9/tests/test_s4_product_persistent_3d.py` runs real SwiftShader WebGL2 and verifies GLB load, camera change, reversible scroll, mobile width and no errors.
- The workflow requires this new result in addition to the old Stage9 tests; keep commercial release on HOLD until tests and visual review pass.

This is a functional camera-continuity implementation, not a validated photoreal artistic scene or feature parity with reference sites. Lighting, pointer-drag control, storytelling art, performance on older devices and material-transition creative direction still require dedicated UX acceptance.
