# Motion Studio Web V1.0 — consolidated R32–R35 handoff

Date: 2026-11-16
Project: Web-only Motion Studio, no desktop installer
Branch: `release/r18-r21-acceptance-gates`
Release state: **CANDIDATE BLOCKED / PRODUCTION NOT PUBLISHED**

## 1. Real project status after batched implementation

| Phase | Delivered | Evidence | Remaining |
|---|---|---|---|
| R32 media quality | Pillow decodes real committed source files; checks SHA, declared native source pixels, presentation upscale, provenance and all 39 chapter slots | [R32 successful source audit](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43890784320) | 33 collage-derived media scenes still require actual individual original-image regeneration and review |
| R33 end-to-end UX | Real Chromium/Firefox/WebKit preview/edit/save/reopen/export tests; R33 extra test checks two-scene original image import then R16 scroll values and exported CSS parity | [R33 3-browser PASS](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43891669262) | Human visual comparison with actual high-resolution images, not synthetic browser fixtures |
| R33 visual evidence | Fresh actual Chromium desktop/mobile screenshots for 8 templates: 68 images (four core shots per template/viewport plus four pilot preview shells). Large PNG artifact retention may fail due to GitHub storage quota | [R33 screenshot geometry PASS](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43892427766); [public compressed gallery deployment](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43893555826) | Separate public browser screenshot gallery release check for new commit |
| R34 candidate gate | Preflight tests SHA-bound explicit approval, human art-direction record, 39 decoded originals, five technical review categories and separate post-deploy live SHA verification | [R34 preflight report](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43892675724) | Image replacement and manual approval remain HOLD; no candidate was promoted |
| R35 deployment safety | Production workflow now builds once, tests the **same HTML** across Chromium/Firefox/WebKit and Three.js/WebGL, then publishes ONLY production-root files without force-pushing away review websites; separate exact-SHA rollback workflow | `.github/workflows/web-release-pages.yml` and `v1-pages-rollback.yml` | NO PRODUCTION DEPLOYMENT (correctly blocked by quality gate) |

## 2. Precisely remaining media scenes (33 total)
- Editorial: 3 (chapters 2–4)
- 3D Product: 4 (chapters 2–5)
- Cinematic: 4 (chapters 2–5)
- Architecture: 4 (chapters 2–5)
- Agency: 5 (chapters 1–5)
- Fashion: 4 (chapters 2–5)
- Gallery: 4 (chapters 2–5)
- SaaS: 5 (chapters 1–5)

The R29 pair are actual independently generated visual-trial images, **not** committed to the 39-scene official production pack. The R30 review page can import them manually into Cinematic chapters 2 and 3. The source manifest remains honest.

## 3. Exact go-live stop conditions

The following must all be established from evidence:
1. Zero collage-derived or unresolved source-native-resolution issues; 39 unique decodable original visual files; correct hashes; provenance/usage terms documented.
2. Genuine visual approval (subject and story continuity, crop, legibility, aesthetic consistency, typography) for all 8 complete templates on desktop and mobile, not just CI passing.
3. Full three-browser and GLB/PBR motion regression on the final candidate with no newly introduced defect.
4. All critical user journeys work: discovery, preview, close/use, editing text/images/interactions, JSON save/reopen, standalone HTML export with no remote runtime dependency.
5. Signed external exact source-commit approval: GitHub Actions repository variable `V1_APPROVED_SOURCE_SHA` equals selected immutable Git SHA. This is stored OUTSIDE the release commit to avoid the impossible self-referencing-commit-SHA problem.
6. Production release can run only on the approved main branch via `web-release-pages.yml`; full deployed HTTPS smoke and SHA check must pass. Keep a historical gh-pages SHA for independent rollback.
7. Do not mark `liveIntegrity` completed until exact deployed-source SHA and browser smoke are observed. GitHub Pages review URLs remain separate from production.

## 4. Cost and credentials (only when user explicitly approves)

A paid image-generation provider must be connected to the R26 workflow using a GitHub Actions secret named `GEMINI_API_KEY` (not sent in chat or committed to the repo). The R26 workflow defaults to cost-free prompt verification and requires explicit `GENERATE_IMAGES` authorization for paid runs.

Official Gemini 3.1 Flash Image listed image output cost: roughly USD 0.101 for a 2K output (33 outputs ≈ USD 3.33 before text tokens, input images, retry overhead, currency charges or failed calls); see https://ai.google.dev/gemini-api/docs/pricing . No budget cap, source art or credential has been authorized during this code batch. Therefore **NO 33-IMAGE GENERATION WAS EXECUTED**.

## 5. Next precise actions, not new indefinite development phases

- Once a provider credential and paid image generation are explicitly authorized, run R26 original-scene workflow with a two-image trial and inspect results; use approved full 33 only after this quality check.
- Import only reviewed image bytes with R25 validated bulk-importer into a draft PR. Run R32 audit, R33 screenshot and E2E again against the exact new commit.
- The human art review record must be approved; then set `V1_APPROVED_SOURCE_SHA` to the final main-branch commit after approval, not before changes.
- Run the fail-closed V1 production Pages workflow. Confirm live SHA and actual browser smoke; if the production root is defective, use the explicit rollback workflow and a prior gh-pages commit SHA.
- Remaining feature ideas become V1.1 backlog, not release blockers unless they break the ten stated V1 DoD criteria.

## 6. Published review channels
- Working source-first review editor: https://mrs-zhong1.github.io/motion-studio-web/r18-ai-review/
- Independent R33 screenshot gallery (only after confirmed publication): https://mrs-zhong1.github.io/motion-studio-web/r33-visual-review/

The green production-preflight *report* workflow explicitly means "the audit ran" and does NOT mean images or the product received production approval.
