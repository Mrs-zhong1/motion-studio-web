#!/usr/bin/env python3
"""Read-only, bounded network diagnosis in the environment running the script."""
import json,socket,urllib.request,datetime,os
from pathlib import Path
hosts=('registry.npmjs.org','cdn.jsdelivr.net','github.com')
result={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hosts':{},'npm_registry':'https://registry.npmjs.org/','environment':'current runtime only; not user device'}
for host in hosts:
 try:
  vals=sorted(set(info[4][0] for info in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)))
  result['hosts'][host]={'dns':'OK','addresses':vals[:3]}
 except OSError as e:
  result['hosts'][host]={'dns':'FAIL','error_type':type(e).__name__,'error_code':getattr(e,'errno',None),'message':str(e)}
Path('R14_NETWORK_DIAG.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps(result,indent=2,ensure_ascii=False))
