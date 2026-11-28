#!/usr/bin/env python3
"""Stamp a browser result with the exact candidate commit tested by the current runner."""
import argparse,json,os,subprocess
from pathlib import Path
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--file",type=Path,required=True);ap.add_argument("--sha");a=ap.parse_args()
    if not a.file.is_file():raise SystemExit(f"result file missing: {a.file}")
    sha=a.sha or os.environ.get("MOTION_CANDIDATE_SHA") or subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    if len(sha)!=40 or any(c not in "0123456789abcdef" for c in sha.lower()):raise SystemExit("candidate SHA must be a full 40-character Git commit")
    doc=json.loads(a.file.read_text(encoding="utf-8"));doc["candidateSha"]=sha;doc["candidateShaSource"]="git rev-parse HEAD after R53 asset persistence"
    a.file.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"file":str(a.file),"candidateSha":sha},indent=2))
if __name__=="__main__":main()
