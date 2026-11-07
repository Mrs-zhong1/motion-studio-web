#!/usr/bin/env python3
"""Verify that the offline artifact really contains a bundled Three runtime.
This check is *not* a proof of WebGL rendering or visual quality.
"""
from pathlib import Path
import json, re, sys
p=Path(__file__).resolve().parent
html=(p/'Motion-Studio-Editor-OFFLINE.html')
checks={}
if html.exists():
    source=html.read_text(encoding='utf-8')
    checks['html_over_300kb']=html.stat().st_size>300000
    checks['offline_js_injected']=bool(re.search(r'window\.MotionThreeOfflineModule\s*=\s*"',source)) and 'window.MotionThreeOfflineModule = null;' not in source
    checks['no_remote_module_imports']=not bool(re.search(r'import\s+.*?from\s*[\'"]https?://',source))
    checks['has_editor_ui']='template' in source and '<html' in source.lower()
else:
    checks['artifact_exists']=False
stats=p/'three-bundle-stats.json'
if stats.exists():
    data=json.loads(stats.read_text())
    checks['bundle_built']=data.get('built') is True and data.get('sourceBytes',0)>100000
else:
    checks['stats_exists']=False
checks['license_exists']=(p/'THIRD_PARTY_THREE_LICENSE.txt').exists()
print(json.dumps({'checks':checks,'passed':all(checks.values()),'scope':'offline bundle contents only'},indent=2))
sys.exit(0 if all(checks.values()) else 2)
