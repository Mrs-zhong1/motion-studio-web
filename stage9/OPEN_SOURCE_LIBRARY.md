# Motion Studio / Open source reference library (2026-11-16)

Seven repositories supplied by the user on ~November 14 are registered in `open-source-library.json`. This is a **reference/adaptation inventory**, not a claim that all seven frameworks or third-party source files are installed.

| Reference | Layer | Status | Action |
|---|---|---|---|
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | L2 | PATTERN_ADAPTER_ONLY | dialog, popover, keyboard-focus, component-token-contract |
| [creativetimofficial/ui](https://github.com/creativetimofficial/ui) | L1+L2 | DESIGN_REFERENCE_ONLY | gallery-card-layout, editor-dashboard-information-hierarchy, template-grid |
| [nuxt/ui](https://github.com/nuxt/ui) | L2 | PATTERN_ADAPTER_ONLY | form-validation, semantic-component-api, design-tokens |
| [cosscom/ui](https://github.com/cosscom/ui) | L2 | DESIGN_REFERENCE_ONLY | compact-properties-panel, dense-data-list, focus-and-layer-controls |
| [ant-design/ant-design](https://github.com/ant-design/ant-design) | L2 | PATTERN_ADAPTER_ONLY | property-inspector, undo-feedback, asset-library-table, form-errors |
| [sveltejs/svelte](https://github.com/sveltejs/svelte) | L3 | ARCHITECTURE_EVALUATION_ONLY | reactive-state-architecture, small-bundle-evaluation |
| [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) | L1+L2 | TOKEN_ADAPTER_ONLY | spacing-scale, responsive-token-map, utility-class-composition |

## Integration rule
Preserve the vanilla single-page editor and self-contained HTML exporter. React, Vue/Nuxt and Svelte component implementations cannot be copied wholesale into the present runtime and still be called a working integration. Adapt specific verified UI patterns (accessibility, state control, panel UX, responsive tokens) as original code. Use Three.js only for scenes where actual WebGL materially helps.

The first implemented S1/S2 change is **a continuous Editorial scene**: four image/text states driven by one scroll progress and rendered in one persistent stage, rather than a stack of unrelated nested iframe demos. Existing 20 registry components remain available as optional authoring tools. This is not yet a Pear-style fabric shader or a Grande Charte glass typography replica.

## S1-S4 delivery criteria
- S1: one persistent story stage, normalized 0-1 timeline, scroll reversibility, reduced-motion fallback and publisher-safe export.
- S2: Editorial Portfolio 4-scene flagship, no neon poster demo beside AI photography, one visible navigation mechanism in preview.
- S3: other 7 templates independently art-directed and transitioned (not simply swap colors and pictures); **pending**.
- S4: preview, Save, Reopen, Export; Three.js and all 20 components remain working; verify in all three browsers, including live preview; **pending final CI**.

Never mark `sourceCopied:true` or claim an open-source library was fully incorporated solely because its name appears here.