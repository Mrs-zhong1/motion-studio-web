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

## Production routing (initial hypothesis; visual review can re-route)

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

The routing is a production hypothesis, not an approval. A source is not acceptable merely because it is free to download.

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
- Keep PR #2 open, draft and unmerged.
