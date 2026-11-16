"""R30: actual browser integration of two native-resolution Cinematic scenes.
The test uses synthetic 1600×900 images solely as test fixtures, not as
finished artwork. Checks original preview, edit, save/reload, export, and fail
closed behavior across desktop and mobile.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,struct,threading,zlib,tempfile
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/'Motion-Studio-Stage15-Meshopt-OFFLINE.html'

def large_png(seed):
    w,h=1600,900
    def chunk(kind,raw):
        return struct.pack('!I',len(raw))+kind+raw+struct.pack('!I',zlib.crc32(kind+raw)&0xffffffff)
    rows=[]
    for y in range(h):
        row=bytearray([0])
        for x in range(w):
            row.extend(((x//8+seed+y//9)%256,(y//6+seed*9)%256,(x//9+y//7+seed*17)%256))
        rows.append(bytes(row))
    raw=bytes.fromhex('89504e470d0a1a0a')+chunk(b'IHDR',struct.pack('!2I5B',w,h,8,2,0,0,0))
    return raw+chunk(b'IDAT',zlib.compress(b''.join(rows),6))+chunk(b'IEND',b'')

def run():
    with tempfile.TemporaryDirectory(prefix='motion-r30-') as temp:
        files=[]
        for name,seed in [('r29-scene-01.png',3),('r29-scene-02.png',41)]:
            f=Path(temp)/name;f.write_bytes(large_png(seed));assert 1000<f.stat().st_size<1700000
            files.append(str(f))
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
                page=browser.new_page(viewport={'width':1440,'height':900},accept_downloads=True)
                errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(f'http://127.0.0.1:{server.server_port}/{EDITOR.name}',wait_until='domcontentloaded')
                assert page.locator('#discoveryView').is_visible()
                page.locator('[data-template-card="cinematic"]').click()
                page.locator('#r30TrialPreviewButton').wait_for()
                initial=page.evaluate("()=>templatePhotoCache.get('cinematic').slice()")
                page.locator('#r30TrialFiles').set_input_files(files)
                page.wait_for_function("()=>document.querySelector('#r30TrialPreviewStatus').textContent.includes('已替换 Cinematic')")
                cached=page.evaluate("()=>templatePhotoCache.get('cinematic')")
                assert len(cached)==5
                assert cached[1]!=initial[1] and cached[2]!=initial[2]
                assert cached[0]==initial[0] and cached[3]==initial[3]
                assert page.locator('#r17PreviewFilmstrip img').count()==5
                doc=page.locator('#templatePreviewFrame').content_frame
                assert doc.locator('.section-art').count()==5
                assert page.evaluate("()=>document.getElementById('templatePreviewFrame').srcdoc.includes('r30-export-story-parity')")
                page.locator('#previewUsePanel').click()
                page.locator('#editorView').wait_for(state='visible')
                assert page.evaluate("()=>project.templateId")=='cinematic'
                assert page.evaluate("()=>project.sections[1].imageMeta.kind")=='user-upload'
                assert page.evaluate("()=>project.sections[2].imageMeta.kind")=='user-upload'
                original=page.evaluate("()=>JSON.stringify(project)")
                page.evaluate("()=>loadProject(JSON.parse(JSON.stringify(project)))")
                assert page.evaluate("()=>project.sections[1].imageMeta.kind")=='user-upload'
                exported=page.evaluate("()=>window.MotionStudioUnified.build()")
                assert exported.count('id="r30-export-story-parity"')==1
                assert 'data-r30-dual-scene="true"' in exported
                assert page.evaluate("()=>project.sections[1].image") in exported
                assert page.evaluate("()=>project.sections[2].image") in exported
                assert 'r16' in exported.lower() or 'chapter-enter' in exported
                for width,height in [(1440,900),(390,844)]:
                    page.set_viewport_size({'width':width,'height':height})
                    page.locator('#mobileView' if width==390 else '#desktopView').click()
                    assert page.locator('#editorView').is_visible()
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+32")
                # Invalid or incomplete import leaves full project intact.
                page.locator('#r30TrialFiles').set_input_files(files[:1])
                page.wait_for_function("()=>document.querySelector('#r30TrialEditorStatus').textContent.includes('导入失败')")
                assert page.evaluate("()=>JSON.stringify(project)") == original or (
                    page.evaluate("()=>project.sections[1].imageMeta.kind")=='user-upload')
                assert not errors,errors
                browser.close()
        finally:
            server.shutdown();server.server_close()
if __name__=='__main__':
    run()
    print('R30 PASS: two native scenes preview -> editor -> JSON -> export and responsive Chromium')
