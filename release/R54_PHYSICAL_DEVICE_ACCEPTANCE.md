# R54 Physical-device acceptance record — required before release

Status: NOT TESTED. Browser automation is not physical-device evidence.

Record one run per device. Do not mark PASS without screenshots/video, device/OS/browser versions, exact candidate SHA, tested URL, timestamp and tester notes.

| Device class | Minimum target | Required checks | Evidence location | Result |
|---|---|---|---|---|
| macOS desktop | Physical Mac, current supported macOS, Safari | Discovery → preview → edit → save → reload → export; WebGL scene; console/network errors; reduced motion; keyboard navigation | attach dated evidence | NOT_TESTED |
| iPhone | Physical iPhone, current supported iOS, Safari | 390px-class viewport; touch targets; safe areas; chapter navigation; scroll performance; WebGL fallback; save/reopen/export | attach dated evidence | NOT_TESTED |
| Android | Physical Android phone, current supported Android, Chrome | responsive layout; touch; scroll; WebGL fallback; save/reopen/export; no horizontal overflow | attach dated evidence | NOT_TESTED |

## Per-run evidence fields

- Candidate commit SHA:
- Deployed HTTPS URL:
- Device model:
- OS version:
- Browser name and version:
- Physical device confirmed (yes/no):
- Test date/time with timezone:
- Screenshot/video evidence:
- Console/network log:
- Tested template set (all eight required):
- Create/edit/save/reopen/export result:
- Known defects:
- Tester:
- Result: NOT_TESTED / PASS / FAIL

## Hard acceptance rules

1. Test all eight templates, not only the Agency and SaaS pilots.
2. Repeat save/reopen/export on each device class.
3. Record failures; do not waive a failed class because desktop Chromium passes.
4. Any missing evidence keeps R54 OPEN.
5. A test performed on a simulator, responsive emulator or Playwright device profile is not physical-device acceptance.
