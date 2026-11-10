#!/usr/bin/env python3
"""Stage16: evidence-based macOS hardware Chrome probe for Stage15 offline export.

Playwright WebKit is NOT Apple's Safari; never report it as Safari acceptance.
Run on the target Mac with locally installed Google Chrome and Playwright.
"""
import argparse, json, platform, sys, time
from datetime import datetime, timezone
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--html", default="stage9/output/STAGE15-MESHOPT-SINGLE-EXPORTED.html")
    ap.add_argument("--out", default="stage9/output/STAGE16-MAC-HARDWARE-RESULT.json")
    ap.add_argument("--screenshot", default="stage9/output/STAGE16-MAC-HARDWARE-CAPTURE.png")
    args=ap.parse_args()
    html=Path(args.html).resolve()
    out=Path(args.out).resolve()
    result={"schemaVersion":1,"test":"Stage16 native macOS Chrome hardware WebGL acceptance",
            "timestampUTC":datetime.now(timezone.utc).isoformat(),
            "platform":platform.platform(),"machine":platform.machine(),
            "sourceHTML":str(html),"chromeHardwareAccepted":False,
            "safariAccepted":False,"safariStatus":"NOT TESTED (requires native Safari)",
            "longRunGpuMemoryAccepted":False,"errors":[]}
    page=None
    browser=None
    try:
        if sys.platform!="darwin":
            raise RuntimeError("Requires macOS for target hardware acceptance; CI Linux is not evidence.")
        if not html.is_file():
            raise FileNotFoundError(str(html))
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            # Use locally installed Chrome, not bundled Chromium/SwiftShader.
            browser=pw.chromium.launch(channel="chrome", headless=False)
            page=browser.new_page(viewport={"width":1280,"height":800},device_scale_factor=1)
            page_errors=[]
            remote=[]
            page.on("pageerror",lambda e:page_errors.append(str(e)))
            page.on("request",lambda req:remote.append(req.url) if req.url.startswith(("http://","https://")) else None)
            page.goto(html.as_uri(),wait_until="domcontentloaded")
            page.wait_for_timeout(1700)
            status_frame=None
            for f in page.frames:
                try:
                    if f.evaluate("Boolean(window.__motionThreeStatus)"):
                        status_frame=f
                        break
                except Exception:
                    pass
            if status_frame is None:
                raise RuntimeError("Exported HTML did not create window.__motionThreeStatus")
            for progress in (0.05,0.27,0.55,0.82,0.98):
                status_frame.evaluate("(p)=>window.postMessage({type:'motion-studio-scroll',progress:p},'*')",progress)
                page.wait_for_timeout(220)
            page.wait_for_timeout(700)
            status=status_frame.evaluate("window.__motionThreeStatus")
            gpu=status_frame.evaluate("""() => {
              const c=document.querySelector('canvas');
              if(!c) return {error:'No canvas'};
              const gl=c.getContext('webgl2');
              if(!gl) return {error:'WebGL2 context unavailable'};
              const ext=gl.getExtension('WEBGL_debug_renderer_info');
              return {webgl2:true,version:gl.getParameter(gl.VERSION),
                renderer:gl.getParameter(gl.RENDERER),
                vendor:gl.getParameter(gl.VENDOR),
                unmaskedRenderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):null,
                unmaskedVendor:ext?gl.getParameter(ext.UNMASKED_VENDOR_WEBGL):null};
            }""")
            page.screenshot(path=args.screenshot,full_page=True)
            result.update({"engineStatus":status,"gpu":gpu,"pageErrors":page_errors,
                           "remoteRequests":remote,"screenshot":str(Path(args.screenshot).resolve()),
                           "chromeVersion":browser.version})
            renderer=(str(gpu.get("unmaskedRenderer") or "")+" "+str(gpu.get("renderer") or "")).lower()
            software=any(x in renderer for x in ("swiftshader","llvmpipe","software","mesa offscreen","basic render"))
            # If debug renderer info is unavailable, do NOT guess hardware success.
            identified=bool(gpu.get("unmaskedRenderer"))
            result["hardwareRendererIdentified"]=identified
            result["softwareRendererDetected"]=software
            result["chromeHardwareAccepted"]=bool(
                gpu.get("webgl2") and identified and not software
                and status.get("engine")=="three" and status.get("webgl2")
                and status.get("pbr") and status.get("meshCount",0)>0
                and status.get("frames",0)>=4 and status.get("visiblePixels",0)>2
                and status.get("pixelDifference",0)>15
                and status.get("error") is None and not page_errors and not remote)
            result["releaseAccepted"]=False
            result["releaseBlockers"]=["Native Safari acceptance missing",
                                        "Long-run GPU memory stability missing"] + (
                    [] if result["chromeHardwareAccepted"] else ["Mac hardware Chrome test failed or inconclusive"])
            browser.close()
    except Exception as e:
        result["errors"].append(f"{type(e).__name__}: {e}")
        result["releaseAccepted"]=False
        result["releaseBlockers"]=["Mac hardware Chrome test failed or not run","Native Safari acceptance missing",
                                   "Long-run GPU memory stability missing"]
        if browser:
            try: browser.close()
            except Exception: pass
    finally:
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding="utf8")
        print(json.dumps(result,ensure_ascii=False,indent=2,default=str))
    return 0 if result["chromeHardwareAccepted"] else 1

if __name__=="__main__":
    sys.exit(main())
