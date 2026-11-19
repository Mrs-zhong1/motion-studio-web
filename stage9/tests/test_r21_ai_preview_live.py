"""R21 true public HTTPS review smoke for the committed 39-AI build."""
import hashlib
import json
import os
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

URL=os.environ.get("MOTION_R18_URL","").rstrip("/")+"/"
assert URL.startswith("https://"),"Public HTTPS review URL is required"

def get(path):
    with urlopen(URL+path,timeout=35) as resp:
        assert resp.status==200,(path,resp.status)
        return resp.read()

def run():
    meta=json.loads(get("REVIEW_BUILD.json"))
    raw=get("index.html")
    digest=hashlib.sha256(raw).hexdigest()
    expected_commit=os.environ.get("MOTION_R18_EXPECTED_COMMIT")
    if expected_commit:
        assert meta.get("sourceCommit")==expected_commit,(meta.get("sourceCommit"),expected_commit)
    assert digest==meta["sha256"] and meta["aiAssetCount"]==39,meta
    assert meta["aiOriginalMedia"] is True
    evidence={"url":URL,"commit":meta["sourceCommit"],"sha256":digest,
              "aiAssets":0,"templates":0,"saved":False,"exported":False,"errors":[]}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1440,"height":900},accept_downloads=True)
        page.on("pageerror",lambda e:evidence["errors"].append(str(e)))
        page.goto(URL,wait_until="domcontentloaded",timeout=60000)
        page.locator("[data-template-card]").first.wait_for()
        summary=page.evaluate("""()=>{
          const ids=['editorial','product-3d','cinematic','architecture','agency','fashion','gallery','saas'];
          return {templates:ids.length,
          chapters:ids.reduce((n,id)=>n+(templateOfflinePhotoBundles[id]?.length||0),0),
          allAI:ids.every(id=>templateOfflinePhotoBundles[id]?.every(x=>x.source?.startsWith('ai-generated://')&&x.media?.startsWith('data:image/'))),
          coversAI:ids.every(id=>templateThumbnailImages[id]?.startsWith('data:image/')),
          components:registry.length};
        }""")
        assert summary=={"templates":8,"chapters":39,"allAI":True,"coversAI":True,"components":20},summary
        evidence["aiAssets"]=summary["chapters"];evidence["templates"]=summary["templates"]
        page.locator("[data-template-card='cinematic']").click()
        page.locator("#previewUse").wait_for(state="visible",timeout=30000)
        page.locator("#previewUse").click()
        assert page.locator("#editorView").is_visible()
        assert page.evaluate("project.templateId")=="cinematic"
        page.locator("#projectName").fill("Motion AI review verified")
        with page.expect_download() as dl:
            page.locator("#saveProject").click()
        project=json.loads(dl.value.path().read_text(encoding="utf-8"))
        assert project["title"]=="Motion AI review verified"
        assert all(x["image"].startswith("data:image/") for x in project["sections"])
        evidence["saved"]=True
        with page.expect_download() as dl:
            page.locator("#exportPage").click()
        exported=dl.value.path().read_bytes()
        # R39 is intentionally leaner than the legacy full editor export.
        # Verify five actual embedded media and five authored frames, not an
        # arbitrary byte count or retired <section class="section"> wrappers.
        assert len(exported)>10000,len(exported)
        assert b"Motion AI review verified" in exported
        assert b'data-r39-film="continuous"' in exported
        assert exported.count(b'class="r39-frame"')==5
        assert exported.count(b'class="r39-caption"')==5
        assert exported.count(b'data:image/')>=5
        assert b"images.unsplash.com" not in exported
        evidence["exported"]=True
        browser.close()
    assert not evidence["errors"],evidence
    print(json.dumps(evidence,ensure_ascii=False,indent=2))
if __name__=="__main__":
    run()
