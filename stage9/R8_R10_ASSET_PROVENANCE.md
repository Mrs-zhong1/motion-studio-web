# Motion Studio — R8/R10 demo asset review

Status: REVIEW ONLY — NOT commercial rights clearance.

## Implementation
- All eight templates now use per-chapter image assets rather than repeated crops of one hero photograph.
- The remote demo fetches one cover and up to two distinct Unsplash photo URLs; every remaining chapter receives original, deterministic Canvas-drawn editorial artwork. On image fetch failure, an original drawing replaces the missing image.
- The offline build keeps its bundled demo cover JPEGs and disables remote secondary photos; extra chapters therefore use original drawn graphics.
- A runtime map named `templateAssetAuditCache` records chapter, kind (`unsplash-photo` or `original-generated-art`), source URL and `rightsReviewed:false`. These labels are not proof of any rights.
- The drawing is original procedural graphic art, not a real photo, custom commissioned art, or final photorealistic work.

## Production blockers
1. Audit and record the source photo page, photographer, download date, release status and intended usage for each photo; do not treat host URLs as completed clearance.
2. Unsplash's general license permits many commercial uses, but recognizable people, visible trademarks, other artworks, and potentially template resale contexts need additional review.
3. Review the origins of the embedded offline cover JPEGs separately. Image binary presence does not establish a license.
4. CI simulates remote photo delivery; this does not prove live host access or image rights.
5. Human visual review of every template's opening, middle and ending chapters is still required.

## Relevant terms
- https://unsplash.com/license
- https://help.unsplash.com/en/articles/2612329-releases-and-trademarks
- https://help.unsplash.com/en/articles/2612317-can-i-use-unsplash-images-as-part-of-a-product-to-sell
