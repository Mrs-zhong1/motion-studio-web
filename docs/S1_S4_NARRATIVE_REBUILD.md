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
| 3D Product Experience | Persistent GLB object | camera orbit, material close-up, lighting state and CTA handoff | drag/orbit | **legacy GLB valid; story integration pending** |
| Cinematic Journey | Same landscape/time sequence | pin, masked filmic reveals, timeline scrub, no snap jump | scroll | pending |
| Architecture Studio | One spatial model/project | exterior→interior→detail camera path | guided orbit | pending |
| Creative Agency | Graphic system of persistent shapes | typographic morph and spatial collage without iframe boundaries | hover/magnet | pending |
| Fashion Editorial | Textile and silhouette | macro→portrait→runway material transition | pointer parallax | pending |
| Gallery Exhibition | Curated collection in spatial context | object plane→gallery→detail | gallery navigation | pending |
| SaaS Product Story | Same interactive UI object | feature transition in place, stateful data walkthrough | controlled UI | pending |

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
