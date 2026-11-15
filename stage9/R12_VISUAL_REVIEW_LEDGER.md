# R12-02 · Eight-template visual review ledger
Generated: 2026-11-15. **Review status: OPEN — no human visual signoff has been recorded.**

This ledger is NOT proof of professional art direction. Use real screenshot/interactive page evidence to identify weak templates before approving release.

## Evidence available
- [52+ screenshots and R11 simulation](visual-evidence/README.md) (first chapter, chapter 3 and ending, desktop/mobile; 2 full preview shell sets)
- [Visual geometry audit](VISUAL_AUDIT_REPORT.md) — prior screenshots show layout and embedded images, not design quality
- [CI run 43709516618](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43709516618) — 3-browser E2E PASS, not creative signoff
- [Preview website](https://mrs-zhong1.github.io/motion-studio-web-pages/) — review build; do not infer current deployment matches the latest source SHA

## Template-by-template decisions
| ID | Template | Opening (desktop/mobile) | Middle chapter | Ending | Preview shell | Art direction | Rights | Decision |
|---|---|---|---|---|---|---|---|---|
| editorial | Editorial Portfolio | Captured | Captured | Captured | Captured | NOT REVIEWED | UNKNOWN | HOLD |
| product-3d | 3D Product Experience | Captured | Captured | Captured | Captured | NOT REVIEWED | UNKNOWN | HOLD |
| cinematic | Cinematic Journey | Captured | Captured | Captured | Preview shell not separately captured | NOT REVIEWED | UNKNOWN | HOLD |
| architecture | Architecture Studio | Captured | Captured | Captured | Preview shell not separately captured | NOT REVIEWED | UNKNOWN | HOLD |
| agency | Creative Agency | Captured | Captured | Captured | Preview shell not separately captured | NOT REVIEWED | UNKNOWN | HOLD |
| fashion | Fashion Lookbook | Captured | Captured | Captured | Preview shell not separately captured | NOT REVIEWED | UNKNOWN | HOLD |
| gallery | Interactive Gallery | Captured | Captured | Captured | Preview shell not separately captured | NOT REVIEWED | UNKNOWN | HOLD |
| saas | Modern SaaS | Captured | Captured | Captured | Preview shell not separately captured | NOT REVIEWED | UNKNOWN | HOLD |

## Visual review rubric — apply to each of 8 templates
1. **Visual differentiation:** distinguish actual typographic system, section rhythm, imagery art direction and composition; changing palette alone is insufficient.
2. **Preview vs reference sites:** visually compare transition timing, scale, overlays and first-screen atmosphere using moving screen recordings, not still screenshots.
3. **Content imagery:** check each chapter has a coherent relevant image, rather than one cropped/repeated demonstration JPG.
4. **Full-page narrative:** first, middle and ending chapters must clearly differ, with purposeful scroll motion.
5. **Editing experience:** template choose → preview → close → choose/use → edit text/media → export without unexpected scroll traps.
6. **Responsive:** no clipped headlines, touch control overlap, horizontal overflow or unreadable card grids.
7. **3D quality:** headphone silhouette, normal/roughness response, camera framing, material transitions and fallback assessed *visually*.
8. **Accessibility:** reduced-motion experience, keyboard navigation, legible contrast, descriptive controls and fallback usable.

Record per finding: template ID; section; viewport; exact repro; browser; screenshot/video evidence; severity P0/P1/P2; proposed edit; resolved commit; reviewer and approval date.

## Release rule
An automated geometry pass can never change any Art direction, Rights or Decision cell to PASS. Approvals require dated inspectable evidence. Default is HOLD.
