# R55 Exact-SHA HTTPS deployment and online acceptance runbook

Status: BLOCKED — do not deploy production while R50 visual review, R52 photo rights, R53 eight-template integration, or R54 physical-device acceptance remain open.

## Preconditions

- [ ] Exact candidate SHA recorded and immutable.
- [ ] R25, R32, R18–R21 and full product E2E are green on that exact SHA.
- [ ] R50 3D/SVG samples passed independent human art-direction review.
- [ ] All 18 procedural assets have reproducible source, native dimensions and unique hashes.
- [ ] All 15 photography assets have itemized commercial-reuse evidence and exact file hashes.
- [ ] R53 eight-template asset coverage and export parity passed.
- [ ] R54 physical Mac, iPhone and Android evidence passed.
- [ ] No unresolved release-gate HOLD or rights uncertainty.

## Deployment record

- Candidate SHA:
- Hosting provider/project:
- Production deployment ID:
- HTTPS URL:
- Deployment timestamp (timezone):
- Build artifact identifier:
- Runtime/config fingerprint:
- Rollback target:

## Live smoke checks

- [ ] HTTPS certificate valid; no mixed content.
- [ ] Fresh browser session can load the public app.
- [ ] All eight template previews render from production assets.
- [ ] Edit one real text field and one visual property in each template.
- [ ] Save, reload and reopen each edited template; verify persisted state.
- [ ] Export HTML for each template and open exported pages independently.
- [ ] Verify Three.js bundle and assets load offline where required.
- [ ] Check browser console and network failures.
- [ ] Check 390px mobile viewport and desktop viewport.
- [ ] Record response status and deployment SHA exposed by the app/build metadata.

## Acceptance

A deployment is accepted only when the deployed SHA exactly equals the tested candidate SHA and every smoke check has attached evidence. A reachable URL alone is not a release pass. Do not merge or promote on a partial result.
