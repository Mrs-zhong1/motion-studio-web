# B1 — Zero-cost local image generation feasibility

Date: 2026-11-19  
Branch: \`release/r18-r21-acceptance-gates\`  
Budget: RMB 0 / USD 0 for image APIs and paid assets

## 1. Confirmed project facts

- R25 requires 33 independent replacement images. The current files are collage crops and must not be relabelled or upscaled.
- The R25 importer validates decoded image bytes, native dimensions, SHA-256 and provenance. It is dry-run by default and only changes committed assets with \`--apply\`.
- The R26 paid Gemini workflow is not part of this B1 path and must remain in dry-run mode. Do not set \`mode=generate\`, pass \`--generate\`, or use any paid endpoint.
- The user device SKU MDE64CH/A is listed as a 14-inch M5 MacBook Pro with 24 GB unified memory and 1 TB SSD. Apple’s M5 MacBook Pro specifications list 24 GB as a supported memory configuration. Confirm the live machine with the local preflight before inference.

## 2. Candidate selection

### Candidate A — FLUX.2 Klein 4B

- Official model card: https://huggingface.co/black-forest-labs/FLUX.2-klein-4B
- Model card license: Apache-2.0.
- MFLUX supports the distilled 4B variant at four inference steps.
- B1 uses MFLUX's 8-bit quantization, \`--small-text-encoder\`, and \`--low-ram\` to reduce memory pressure. The small text encoder is a separate Apache-2.0 Qwen3-0.6B encoder plus an Apache-2.0 adapter according to MFLUX's documentation.
- This is the first candidate to benchmark because it is a compact current model with explicit commercial-use terms.

### Candidate B — Z-Image-Turbo

- Official model card: https://huggingface.co/Tongyi-MAI/Z-Image-Turbo
- Model card license: Apache-2.0.
- Official project describes a 6B model distilled to eight function evaluations and lists very high visual quality, while also noting lower output diversity.
- MFLUX supports local Apple MLX inference. B1 uses 8-bit quantization and low-RAM mode.
- This is the comparison candidate for photographic realism and prompt adherence.

### Excluded candidate — FLUX 3 Image Klein

- Not selected for a zero-cost commercial production route. Its model card uses the FLUX Kommunity License v1.0, not Apache-2.0; commercial output generation is conditional and qualifying-user restricted. The BFL product page also says running it in a product requires a commercial license. Do not substitute it without separate legal review.

### Runtime

- MFLUX project: https://github.com/mflux-community/mflux
- MFLUX source code license: MIT.
- MFLUX runs image models locally on Apple Silicon using MLX; no hosted image API is required.
- Apple states that MLX requires macOS 26.2 or later to use the M5 GPU Neural Accelerators. On an earlier macOS version, do not assume that this specific M5 acceleration is active; the pilot still records the actual OS version and measures real inference time.
- Model weights are large downloads. The pilot checks for at least 40 GB free disk space before running. Network data transfer and electricity are not API charges, but are not literally cost-free in all circumstances.

## 3. Pilot design

The committed runner is \`stage9/generate_r26_local_pilot.py\`.

- Default invocation is a dry-run: it prints the planned commands and does not download weights or generate images.
- Explicit \`--run\` invokes local MFLUX commands only.
- Two models × four representative scenes = eight pilot images:
  - editorial / chapter 2
  - product-3d / chapter 3
  - cinematic / chapter 2
  - architecture / chapter 2
- All outputs target 1792×1008 pixels: exact 16:9 and dimensions divisible by 16.
- Outputs are written outside the repository to \`~/MotionStudio-R26-B1-Pilot\`.
- Each model is run sequentially to avoid loading two large models simultaneously.
- The runner records native dimensions, runtime, seed, model/license reference and SHA-256.
- It stops if a generated output is below 1600×900 or has an unexpected aspect ratio. It does not upscale or resize.
- Pilot output is explicitly marked \`releaseEligible=false\`; it is not a replacement manifest and is never copied into \`stage9/ai-assets\`.

## 4. Local setup and execution

Run on the M5 Mac after confirming at least 40 GB free on the volume containing the output folder.

Install the open-source local runner:

\`\`\`bash
uv tool install --upgrade mflux
\`\`\`

From a local checkout of this branch:

\`\`\`bash
python3 stage9/generate_r26_local_pilot.py
\`\`\`

That first command is dry-run only. When the planned commands and output path look correct, run:

\`\`\`bash
python3 stage9/generate_r26_local_pilot.py --run
\`\`\`

To test one candidate first:

\`\`\`bash
python3 stage9/generate_r26_local_pilot.py --models flux2 --run
\`\`\`

or

\`\`\`bash
python3 stage9/generate_r26_local_pilot.py --models zimage --run
\`\`\`

The first run downloads model weights from Hugging Face. The script does not call Gemini, Replicate, Fal, or any other hosted image API.

## 5. B1 acceptance criteria

B1 is not complete until the local pilot has actually run on the user's Mac and the evidence has been reviewed.

| Gate | Required evidence |
|---|---|
| Hardware preflight | arm64 macOS, actual unified memory, at least 40 GB free disk |
| Local inference | at least one candidate completes without OOM, crash or repeated manual intervention |
| Native resolution | all accepted samples decode at ≥1600×900 without upscaling |
| Composition | subject, scene continuity and requested text-safe area are usable |
| Quality | no severe anatomy/material/texture artifacts; adequate photographic or art-directed quality |
| Variety | distinct scenes and styles do not collapse into generic repeated compositions |
| Cost | no paid API, subscription or asset purchase |
| Provenance | pilot manifest includes model ID, license URL, seed, prompt hash or source storyboard reference, native dimensions and SHA-256 |

If one model fails, retain the evidence and evaluate the other. Do not automatically lower resolution, relax the quality gate, or change the existing 33-image inventory.

## 6. Safety and non-goals

- No paid image generation.
- No API keys or credentials required.
- No modifications to the 39 committed chapter assets or \`stage9/ai-assets/manifest.json\`.
- No approval status changes.
- No production deployment or PR merge.
- No claim of B1 PASS until a real local run and visual review are complete.

## 7. Sources checked on 2026-11-19

- Apple MacBook Pro M5 specifications: https://support.apple.com/en-ie/125405
- MDE64CH/A configuration listing: https://cn.ingrammicro.com.cn/site/productdetail?id=A311-BA48448
- FLUX.2 Klein 4B model card and Apache-2.0 license: https://huggingface.co/black-forest-labs/FLUX.2-klein-4B
- Z-Image-Turbo model card and Apache-2.0 license: https://huggingface.co/Tongyi-MAI/Z-Image-Turbo
- MFLUX installation, model support and quantization: https://github.com/mflux-community/mflux
- FLUX 3 Image Klein license and commercial restrictions: https://huggingface.co/black-forest-labs/flux-3-image-klein


## Superseded production route — 2026-11-20

This B1 FLUX.2 Klein / Z-Image-Turbo local inference proposal is retained as historical feasibility research only. It is **not the approved production route** and must not be started as part of the current release batch.

The user-approved R26 production baseline is now:
- 18 original procedural scenes: Agency 5, Product 3D 4, Gallery 4, SaaS 5.
- 15 commercially redistributable photographs: Architecture 4, Cinematic 4, Editorial 3, Fashion 4.
- No paid image APIs, paid asset purchases, subscriptions or renewed long FLUX/MFLUX model downloads.
- The Blender pilot is review-only. Its output is not production-eligible and must not be imported before visual review, itemized rights review and strict R25/R32 validation.
- SaaS procedural scenes are to be produced as original vector/canvas scenes, not as Blender renders.
- A model card's permissive license does not replace per-asset commercial and distribution review.

If this historical B1 route is ever reconsidered, it requires a separate explicit user decision and a new cost/quality review. Do not infer approval from the presence of this document.
