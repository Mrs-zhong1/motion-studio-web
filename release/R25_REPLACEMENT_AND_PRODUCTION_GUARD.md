# R25 — Native-quality media replacement and production guard

## Delivered
- `release/check_release.py`: production eligibility now also checks 39 individual original-generation source records, source native dimensions >= 1280×720 and max enlargement <= 1.25. Existing 33 collage derivatives cannot pass simply because somebody changes the approval status. Human art direction remains a separate gate.
- `release/test_release.py`: explicit regression where otherwise green approvals with one collage-derived low-native-resolution image must FAIL.
- `stage9/replace_ai_chapters_r25.py`: batch replacement utility. Validates supplied JPEG/PNG bytes (Pillow actual decode), native dimensions, provenance, exact existing chapter filename, and changed SHA-256. Default dry-run; `--apply` updates manifest and image bytes with pre-write backup, and restores the previous files if write fails.
- `stage9/tests/test_r25_replacements.py` and `.github/workflows/r25-native-replacement.yml`: replacement/rollback-oriented smoke and production-HOLD tests.

## Verified workflow evidence
- [R25 replacement safety PASS](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43866873081).
- [R24 real screenshot capture PASS](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43863507102).
- [R24 image-quality risk audit PASS (audit execution only)](https://github.com/Mrs-zhong1/motion-studio-web/actions/runs/43863366239).

## Replacement input
A local `replacement.json` array with entries specifying `template`, `chapter`, `file`, `source: "AI_GENERATED"`, `sourceType: "individual-generation"`, `trueHighResolutionGenerated: true`, `nativeSourceDimensions: [width,height]`, `generationSystem`, `generationDate`, `sourceReference`, `termsUrl`, and `commercialUseTermsChecked: true`, plus the actual referenced image files in the same folder. Source declarations must be factually accurate and supported.

Install Pillow in the environment, then:
```sh
python stage9/replace_ai_chapters_r25.py /path/to/replacements
python stage9/replace_ai_chapters_r25.py /path/to/replacements --apply
python stage9/tests/audit_r24_source_quality.py --enforce
```
No replacement is made unless `--apply` is passed. Review changes, commit files and updated manifest, rebuild strict AI-only HTML, and run browser CI. Backup remains on disk.

## Outstanding and honest release gate
- Existing repository still has **33 collage-derived images** requiring real independent replacement; this work introduced the validated safe replacement path but did **not** generate 33 source images.
- Metadata and native pixel dimensions are necessary, but not sufficient, for art-quality approval. The workflow cannot establish whether a generated image depicts the same subject or follows the story arc.
- Human review of all 8 templates with opening/middle/ending, scroll/camera, mobile legibility, and full-resolution photography is pending.
- No merge to production or live R25 build claimed. **Production HOLD**.
