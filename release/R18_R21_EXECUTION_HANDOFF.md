# Motion Studio Web — R18 to R21 release handoff

**Scope:** browser-only Web app, eight complete scroll templates, 20 pre-existing motion components. No macOS DMG or physical iOS/Android GPU acceptance.

## Verified automated results

- R18–R21 release unit gate: PASS at [run 43813022364](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43813022364).
- R19 full Stage9 Three.js / GLB / WebGL: PASS at [run 43812402815](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43812402815), commit `d5a02590f9efade8bd74a9ca70989297cb515865`.
- R20 Chromium / Firefox / WebKit Web Product E2E: PASS at [run 43812405742](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43812405742), same commit.
- Screenshot self-commit on PR CI was disabled in `6b18cff21f22cdc93da070e3bc15f1e7c02baad1` to prevent build SHA drift; review evidence publishing is now restricted to explicitly dispatched runs from the legacy review branch.

## R18 media package — full-screen *presentation*, not native detail

A locally assembled ZIP `MotionStudio_R18_Fullscreen_39_Integration.zip` exists on the conversation surface, containing `stage9/ai-assets/manifest.json`, 39 JPEG files, and `release/R18_ASSET_TECHNICAL_AUDIT.json`.
All JPEGs were decoded successfully, are 1600×900, and match their manifest SHA-256. Of the 39, 6 came from separate higher-resolution originals; the remaining 33 were AI collage crops adapted with upscaling and cinematic blurred framing. This is **not** 33 native high-resolution AI generations and does not establish a professional art-direction pass.

**Important blocker:** the source repository's `stage9/ai-assets` directory is still absent as of this handoff. Do not mark AI media integrated in GitHub or publish a final release from the demo-photo fallback.

## Once the package reaches the source checkout

1. Run `python release/install_ai_pack.py /path/to/MotionStudio_R18_Fullscreen_39_Integration.zip --checkout .` (or unpack the `stage9/ai-assets` directory directly).
2. Commit **all** 39 media files plus `stage9/ai-assets/manifest.json` onto a review branch. Do not commit unrelated secrets.
3. Run `node stage9/test_ai_chapter_assets.mjs`, `MOTION_REQUIRE_AI_ASSETS=1 node stage9/build-offline.mjs`, `python -m unittest discover -s release -p 'test_*.py'`, and the browser regression workflows.
4. Review actual **eight complete page sequences** for typography, photographic sharpness, composition, camera transitions and 3D fidelity. Reject the crops if softness is visible; replace with independent full-resolution original AI scenes.
5. Attach immutable CI and preview URL evidence to `release/R18_R21_APPROVALS.json` only after checking all facts. Set the AI media `assetCount` to 39 and `verifiedOrigin` to `AI_GENERATED` only with actual file hashes.
6. Require `python release/check_release.py --mode production` to return 0 and confirm the public HTTPS export's SHA-256 equals the tested build. Only then merge/release.

## Active status

- **R18:** media package verified *outside* GitHub; source integration and visual signoff **HOLD**
- **R19:** Stage9 full browser 3D acceptance **PASS** on pinned commit, final AI build performance pending
- **R20:** three-browser E2E **PASS** on pinned commit; final AI build regression pending
- **R21:** production deployment **HOLD**, pending integrated media and full release gate

No native phone hardware test or unrelated third-party demo-photo license approval is a release condition. Commercial-use policy and disallowed branded/person likeness remain relevant for the AI source media themselves.
