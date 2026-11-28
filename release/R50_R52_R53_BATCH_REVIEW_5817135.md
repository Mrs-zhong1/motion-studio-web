# R50–R53 focused batch review — exact SHA 5817135cb0b5429f3a13786874c9d1cc262fd7de

Review date: 2026-11-21  
Evidence source: GitHub Actions run 44744340107, artifact 14635775577  
Branch: `design/r43-immersive-template-system`

## R50 — visual triage (AI-assisted inspection; not user or legal approval)

| Candidate | Observation | Disposition |
|---|---|---|
| Agency | Three campaign panels exist, but read as a product/interior display wall rather than a differentiated agency case-study journey. No evidence of case switching or scroll narrative in the still. | HOLD — revise composition and prove browser motion |
| Product 3D | Camera is legible with a focal hierarchy, but remains a single still. | HOLD — needs multi-state scene and interaction evidence |
| Gallery | Sculptural objects are visible, but the environment remains a static diorama; gallery visitor navigation and chapter transitions are unproven. | HOLD — revise spatial storytelling and prove navigation |
| SaaS | Clean dashboard hierarchy, but it is a static SVG with illustrative metrics/projects. | HOLD — implement real Capture → Shape → Deliver interactions and mark demo data clearly |

All four manifest rows remain `HUMAN_VISUAL_REVIEW_REQUIRED`, `productionEligible=false`, and `commercialUseTermsChecked=false`. No approval is inferred.

## R52 — evidence and download

- Rights register: 15 required photography slots.
- Candidate ledger: 8 leads total; 1 explicitly rejected for visual mismatch; at most 7 candidates remain for review.
- Latest run downloaded 0 originals; 6 requests failed with HTTP 429.
- Rights validator: 15 rows, 0 accepted, status HOLD.
- This is insufficient source coverage even if every remaining candidate downloads successfully. Additional independently verified candidate sources are required.
- Downloader retry handling is hardened in this commit: 7 attempts, exponential backoff, numeric/date-form Retry-After support, a descriptive project User-Agent, and explicit review-only status.

## R53 — production asset register

- Required slots: 33.
- Accepted slots: 0.
- The register remains fail-closed. Empty file paths, absent local hashes, absent source provenance, and missing explicit human visual approvals remain blockers.
- Do not set `humanVisualApproval`, `productionEligible`, or `reviewStatus=APPROVED` by automation.

## R47/R48, R54/R55

- R47 passed save/reopen/export parity across Chromium, Firefox and WebKit on the inspected SHA.
- R48 is `PASS_CANDIDATE_ONLY`, not release approval.
- R54 requires physical-device evidence.
- R55 requires an actual deployment target, exact deployed SHA verification, HTTPS, and live smoke tests.
- PR #4 remains Draft and must not be merged or published by this batch.

## Gate decision

Overall: **HOLD**. The deterministic browser/build checks are green, but R50 visual direction, R52 rights/source coverage, R53 original assets and approvals, R54 device evidence, and R55 deployment evidence are not complete.
