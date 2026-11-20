# R49 — Four-gate release closure plan

Date: 2026-11-20
Candidate branch: `design/r43-immersive-template-system`
Candidate at start of this closure batch: `fdae2be18e39e26e9bd379366479350a0a7b7794`
Decision: KEEP PR #4 OPEN + DRAFT. No merge or production deployment.

## Verified candidate evidence

- PR #4 remains open, draft and mergeable.
- Product E2E run `44685130534`: Chromium, Firefox and WebKit jobs all succeeded on the candidate SHA.
- Stage 9 standalone Three.js / strict GLB WebGL run `44685123953`: succeeded on the candidate SHA.
- R18-R21 release-review run `44685130430`: succeeded; its success is a review-gate result, not a human release signoff.
- R47 round-trip and R48 candidate-only PASS were reported in the PR's 2026-11-20 consolidated audit. R48 is explicitly `PASS_CANDIDATE_ONLY`, not production approval.

## Gate 1 — Media

Approved production route:
- 18 procedural originals: Agency 5, Product 3D 4, Gallery 4, SaaS 5.
- 15 commercially redistributable photographs: Architecture 4, Cinematic 4, Editorial 3, Fashion 4.

Hard requirements:
- Every slot is a distinct original, >=1600x900 native pixels, 16:9 within the validator tolerance, unique SHA-256, readable JPEG/PNG.
- Procedural files record renderer/source reference/date and explicitly state `thirdPartyAssets=false`.
- Photography records original source URL, creator, exact license ID/URL, attribution, download timestamp and native dimensions.
- No collage crops, upscales, paid image APIs, paid asset purchases or resumed long FLUX/MFLUX generation.
- The four-scene Blender pilot is a visual-review prerequisite before expanding the procedural batch to 18.

Current state:
- The earlier Pillow geometric pilot was rejected as too schematic; it is not production media.
- Blender pilot run `44501248194` failed before rendering because Ubuntu mirrors returned HTTP 503 during package installation. No image artifact was produced.
- The retry-hardened workflow is now enabled on this PR branch. Current run: `44690965370`.
- No media replacement or production eligibility flag has been changed.

## Gate 2 — Rights and authorization

- The current asset manifest records 39 distributed scene images, of which 33 are collage-derived crops from six composite source images; the remaining six are individually generated.
- The existing rights ledger still marks distributed photography, fonts, dependencies and certain model assets as NOT VERIFIED / UNKNOWN.
- For the 15 photography replacements, use only CC0, Public Domain, CC BY or CC BY-SA after compatibility review. Reject NC, ND, missing, unclear or merely free-to-download terms.
- Independently audit the rights of the six retained AI-generated images, procedural model sources, font files, Three.js and every other vendored dependency.
- A technical asset validator or image-generation terms URL does not itself constitute itemized legal clearance.
- Do not set `mediaRightsApproved=true` until every distributed item has evidence and a named human reviewer.

## Gate 3 — Native Safari and physical devices

Required manual evidence:
- User's Apple Silicon Mac: native Safari and native Chrome; actual GPU renderer, not SwiftShader.
- Physical iPhone: iOS Safari.
- Physical Android: Chrome.
- All eight templates: browse, edit, replace image, save, reopen, export and open exported HTML.
- Product 3D: rotate, materials, camera presets, context-loss fallback.
- 30-minute active interaction observation with device/OS/browser/build SHA, screenshots or video, diagnostics, defects and reviewer.
- CI WebKit is not Safari; desktop emulation is not a physical phone. These tests remain NOT TESTED until the evidence is attached.

## Gate 4 — Production HTTPS

The existing `.github/workflows/web-release-pages.yml` is fail-closed:
- Requires SHA-bound approval and R32 original-media audit.
- Builds one exact candidate artifact and tests Chromium, Firefox, WebKit and GLB/WebGL before publishing.
- Publishes the exact tested bytes, then waits for the exact source SHA at the Pages URL and runs live HTTPS edit/save/export smoke.
- A Pages URL or HTTP 200 alone is not acceptance; the served HTML hash and `WEB_RELEASE.json` must match the tested artifact.

Current state:
- No successful current production Pages deployment and no live HTTPS smoke artifact are attached to this candidate.
- Do not manually bypass the preflight or publish this draft candidate.
- Pages configuration and workflow dispatch permissions must be verified by a repository administrator when the candidate is eligible.

## Work performed in this closure batch

- Hardened the Blender pilot workflow with full apt transaction retries and longer network timeouts after the observed HTTP 503 failure.
- Added the current PR candidate branch to the workflow's push trigger so the retry can run without requiring an unavailable workflow-dispatch action.
- Updated the hybrid asset plan to record the user's approved 18 procedural / 15 licensed-photo split and to remove the obsolete PR #2 reference.
- Preserved fail-closed behavior: no replacement assets imported, no rights marked approved, no device signoff fabricated, no deployment or merge.

## Remaining external evidence

1. Review the four Blender pilot images in the Actions artifact once run `44690965370` succeeds. Only then authorize the 18-slot procedural batch.
2. Complete and attach the 15-photo source/license manifest and all retained asset/dependency/font rights evidence.
3. Perform the physical-device test matrix and attach the signed evidence to this exact candidate SHA.
4. Run the production Pages workflow only after gates 1–3 are genuinely closed; attach the exact deployed SHA, live smoke JSON, served artifact hash and rollback reference.

A green CI run, a completed documentation update, or a generated pilot image cannot replace human visual review, rights clearance, physical-device testing or live production acceptance.
