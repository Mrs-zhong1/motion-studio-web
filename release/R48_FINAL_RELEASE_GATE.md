# R48 — Release candidate acceptance gate
- 日期：2026-11-19
- 本阶段不自动合并，不自动发布。
## Hard gates
1. Build: offline standalone editor builds without syntax/runtime build errors.
2. R44: single-canvas preview; all controls remain reachable after removing the information rail.
3. R45: eight template families retain differentiated art direction while scene content is integrated.
4. R46: responsive, keyboard focus, touch targets, reduced-motion and overflow rules.
5. R47: eight-template save → reset → reopen → standalone export parity.
6. Existing visual audit: all eight templates × desktop/mobile screenshots, geometry and image coverage.
7. Browser matrix: Chromium, Firefox and WebKit; all blocking jobs green.
8. Evidence: attach CI run links, generated visual audit report, round-trip report and unresolved defects.
## Release decision
- [ ] All blocking CI jobs green on the same PR head SHA.
- [ ] R44/R45/R46/R47 acceptance reports reviewed.
- [ ] No unresolved P0/P1 visual or interaction defects.
- [ ] Template imagery licensing/provenance reviewed; demo CDN images are not presumed commercially cleared.
- [ ] User explicitly approves merge/release.
## Current state
R48 is a release gate definition only. It does not represent a release approval or a claim that all prior stages have passed.