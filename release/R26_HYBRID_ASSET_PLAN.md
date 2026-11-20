# R26 Hybrid Asset Production Plan — zero paid spend

Date: 2026-11-19  
Branch: `release/r18-r21-acceptance-gates`  
Budget: RMB 0 / USD 0 for image APIs, model subscriptions and paid assets.

## Decision

Replace the former AI-only production dependency with a hybrid, provenance-first pipeline. The first four outputs are review pilots only; none may replace committed assets or change release approval.

## Inventory

The original 33 flagged slots remain unchanged:

- agency: chapters 1–5 (5)
- architecture: chapters 2–5 (4)
- cinematic: chapters 2–5 (4)
- editorial: chapters 2–4 (3)
- fashion: chapters 2–5 (4)
- gallery: chapters 2–5 (4)
- product-3d: chapters 2–5 (4)
- saas: chapters 1–5 (5)

Total: 33.

## Production routing (user-approved baseline, 2026-11-19; visual review may re-route individual slots)

| Template | Slots | Preferred route | Rationale |
|---|---:|---|---|
| agency | 5 | Procedural 3D / vector scene | Art direction already calls for studio-made sculptural props and bold color |
| product-3d | 4 | Procedural 3D scene | Materials, lighting, device geometry and product-stage continuity can be controlled |
| gallery | 4 | Procedural 3D / vector scene | Sculptural installations and gallery plinths are reproducible as original scenes |
| saas | 5 | Procedural Canvas / SVG scene | Abstract data, spatial panels and non-literal product visualizations do not need stock photography |
| architecture | 4 | Open-licensed original photography first; procedural architectural scene fallback | Real built-space credibility matters; require exact source and license metadata |
| cinematic | 4 | Open-licensed landscape / environment photography first | Natural atmosphere and continuity are difficult to fake with flat graphics |
| editorial | 3 | Open-licensed editorial still-life / studio photography first | Tactile material detail and photographic realism are important |
| fashion | 4 | Open-licensed fashion / textile photography first; procedural drape study fallback | Human form, fabric and garment texture need credible visual references |

The 18 procedural / 15 licensed-photography split is the approved production baseline. Individual files still require technical validation and human visual review. A source is not acceptable merely because it is free to download.

## First pilot

Four representative scenes are generated locally by `stage9/r26_hybrid_pilot.py`:

- editorial / chapter 2
- product-3d / chapter 3
- architecture / chapter 2
- agency / chapter 1

The pilot is deterministic and uses Pillow geometry only. It generates native 1600×900 PNG files with unique SHA-256 hashes. It makes no API calls, downloads no model weights, and uses no third-party images. These renders are visual-direction prototypes, not final photography or approved production media. The script writes `commercialUseTermsChecked=false` because a project-level rights review is still required; do not silently promote them through the old AI-only importer.

## Rights and quality requirements

Every final slot must have one of these explicit source routes:

1. `procedural-vector-render` / `procedural-3d-render`: exact renderer version, source scene, seed/configuration, native output dimensions, SHA-256, and a clear statement that no third-party visual assets were embedded.
2. `open-licensed-photography`: exact original source URL, creator, source page, license identifier and URL, attribution text, download timestamp, original pixel dimensions and SHA-256. Allow only licenses explicitly permitting commercial reuse (CC0, public domain, CC BY or CC BY-SA after compatibility review). Reject NC, ND, unclear, missing, or merely “free download” terms.

All final files must be independent originals, native >=1600×900 for R26 visual review (never upscaled), 16:9 or within the existing approved ratio tolerance, unique bytes, readable JPEG/PNG, and pass the title-safe composition check. A technical pass does not constitute art-direction approval.

## Stage gates

- H0 inventory and route map: documented; 33 slots accounted for.
- H1 zero-cost pilot: 4 actual samples generated, hashes/dimensions checked in CI artifact.
- H2 human visual review: HOLD until user reviews the four images in context.
- H3 batch production: only after H2 route approval; produce all 33 to a staging artifact.
- H4 provenance / native-origin validator: all 33 pass; update the R25 importer and R32 auditor to accept explicit non-AI source classes without weakening resolution or hash checks.
- H5 integration: create isolated draft media PR with backups; no direct production-root writes.
- H6 browser regression / release: run Chromium, Firefox and WebKit; preserve R18 art direction and R21 live-integrity HOLD until their actual evidence passes.

## Hard constraints

- No Gemini, Runway, Replicate, Fal, hosted image generation or paid credits.
- Do not resume FLUX.2 downloads as a dependency. Existing Hugging Face cache may remain untouched.
- Do not replace any of the 39 committed images in this pilot.
- Do not mark any approval PASS from a script-generated result.
- Keep PR #4 open, draft and unmerged. Do not merge or publish until all four release gates close.

## Pilot review outcome — 2026-11-19

The first four-scene Pillow geometry prototype completed CI integrity checks (four 1600×900 PNGs, unique hashes, zero paid calls). Visual inspection found the result too flat and schematic for the premium photographic / 3D direction. **Those four renders are rejected as production candidates** and must not enter the media pack. They remain only as proof that the no-cost staging and validation path works.

A second pilot now uses Blender Eevee with original procedural geometry, materials, softbox lighting and camera composition for the same four representative scenes. Its workflow is review-only; even a technical PASS does not grant commercial rights approval or art-direction approval. The Blender pilot must be visually inspected before expanding procedural 3D to the 18 candidate slots.

## CI environment correction — 2026-11-19

The first Blender CI attempt passed both source-safety and 33-slot validator tests, then aborted at renderer startup because the Ubuntu runner lacked `libEGL.so.1` (exit 134). This is an environment dependency failure, not a generated-image quality result.

The workflow now explicitly installs Mesa/EGL/OpenGL runtime libraries (`libegl1`, `libgl1`, Mesa software drivers and required X11 runtime libraries) and runs headless Blender with `EGL_PLATFORM=surfaceless`, `LIBGL_ALWAYS_SOFTWARE=1`, and the llvmpipe software driver. The retry run `44501248194` completed with failure during Blender installation: Ubuntu archive/security mirrors returned repeated HTTP 503 responses for Blender dependencies. This is an infrastructure download failure, not a render-quality result; no rendered images or artifacts were produced. A further workflow hardening commit (`2ce0ff8`) now retries the complete apt update+install transaction with longer network timeouts and is enabled on the current PR #4 candidate branch. Do not proceed to the 18-slot expansion until four actual PNGs pass technical checks and human visual review.


## Approved execution route — clarified 2026-11-20

The user approved the following 33-slot split; this supersedes the earlier FLUX/MFLUX local-inference exploration as the production route:

- **18 original procedural scenes**: Agency 5, Product 3D 4, Gallery 4, SaaS 5. Use Blender/Eevee for dimensional scenes and original Canvas/SVG for SaaS/data-led visuals. All scene sources must be committed and independently reproducible.
- **15 commercially redistributable photographs**: Architecture 4, Cinematic 4, Editorial 3, Fashion 4. Use only CC0, Public Domain, CC BY or CC BY-SA after compatibility review. Each file requires creator, source-page URL, exact license URL, attribution, original dimensions, download timestamp and SHA-256.
- **No paid APIs, subscriptions or asset purchases. Do not resume long FLUX.2 / MFLUX generation.** Existing model cache may remain untouched; it is not a dependency for the approved route.
- The four-scene Blender pilot is still a prerequisite for visual review. Its latest retry failed before rendering due HTTP 503 package mirror errors; therefore there are no Blender pilot images to approve yet.
- Once the four pilot renders exist, human visual review is required before expanding procedural production to 18 slots. The 15 photography slots can be researched and rights-screened in parallel, but no downloaded photo is accepted until its exact license and source evidence are recorded.
- This plan remains a technical production route, not commercial legal advice or a release approval.


## Blender pilot result — 2026-11-20

Run `44690965370` completed successfully and produced four distinct 1600×900 PNG files. The workflow independently verified file decoding, PNG format, native pixel dimensions and unique SHA-256 hashes. Artifact: `r26-blender-3d-pilot-2ce0ff8fb68849cbdca559ccffaf37ddece31a56`.

**Technical result: PASS for the four-file review artifact only. Art-direction result: REJECTED / NOT PRODUCTION-SUITABLE.**

The visual inspection found the current renders too primitive and schematic for the premium visual baseline:
- Agency: floating basic geometric props; insufficient material depth and art direction.
- Product 3D: generic box-like audio object and oversized halo; not a convincing premium product render.
- Editorial: simple tabletop primitives, not a convincing editorial environment.
- Architecture: block-like building and sphere-canopy trees; not architectural photography quality.

The four images are renderer smoke tests only. They are not approved samples, must not enter the 33-slot asset pack, and do not authorize expansion to the 18-scene batch. Editorial and Architecture are also in the approved 15-photo route, not the 18 procedural-scene allocation; their inclusion in this first smoke test was exploratory only.

Next engineering iteration must replace the primitive scene compositions with higher-fidelity, scene-specific art direction and align the pilot slots to the approved procedural categories (Agency, Product 3D, Gallery, SaaS vector). SaaS must use original SVG/Canvas scenes, not Blender. Keep all generated output review-only until human review and rights evidence are complete.
