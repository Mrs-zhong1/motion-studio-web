# R38 — Eight distinct template directions and full five-act Cinematic

Date: 2026-11-17
Branch: `release/r18-r21-acceptance-gates`

## What changed in the real Web project

- `stage9/r38-eight-art-directions.mjs` adds eight **separately scoped** layout, typography, material and interaction-direction families rather than a single full-bleed design shared across templates.
- `stage9/build-offline.mjs` injects the new director after R37 into the same preview → template selection → editor → save → exported HTML chain.
- Cinematic retains its existing **five authored narrative chapters**, now handled as five R37 single-stage sections rather than the earlier two-scene standalone demo. The R37 browser test was corrected to measure *completed instant scroll* rather than read halfway through CSS smooth scrolling.
- Editorial keeps asymmetrical print spreads, Product 3D retains interactive WebGL product canvas, Architecture uses technical grid and project geometry, Agency uses bright skewed poster compositions, Fashion uses portrait lookbook geometry, Gallery uses framed exhibition walls, SaaS uses modular UI/data layers. Do not flatten these into variants of the same photo/title design.
- Existing component library, source photos, R16 chapter camera, JSON project model, original custom 3D and export are preserved; this batch does not claim professional art-direction signoff or replace low-native-resolution collage sources.

## Actual browser evidence

- [R38 unique template directions and real five-chapter Cinematic scroll: PASS](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/44009010135)
  - Eight different template family identifiers, eight different direction/interaction definitions, browser computed background/font/image composition and eight preview/export outputs verified
  - Cinematic count **5**; native stage sticky top constant under actual scroll; redundant iframe mini-demonstrations hidden and single story heading per chapter
  - Desktop/mobile R37 sticky stage checks pass, original R16 progress remains live
- [R36 pilot integration regression: PASS on R38 SHA](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/44009010126)
- Review deployment and complete Chromium/Firefox/WebKit regression must be checked independently. Green director tests are not proof of complete production readiness.

## Human review checklist

Use the review page (once the latest SHA is deployed) and open each template:
1. Cinematic — scroll all **five** chapters, verify one visual subject/title at a time, graceful transitions, compact nav, full camera hold.
2. Product 3D — physically meaningful WebGL object and pointer lighting; no redundant unrelated metal photo vs green-ball demo.
3. Editorial — editorial spreads and offset imagery, not cinematic full-bleed.
4. Architecture — spatial photographs with true drawing grid.
5. Agency — deliberate playful typography/bright layered posters.
6. Fashion — tall lookbook image and graceful type layout.
7. Gallery — curated framed artworks rather than the same giant hero.
8. SaaS — modular features, dashboards and product interface clarity.

## Release status

This is an **interactive review version**. The 33 collage-derived source JPEGs still lack high-resolution original replacements and manual visual acceptance. Production gate remains **HOLD**. Screenshots/real review are needed before all eight families can be marked aesthetically approved.
