"""CodeMap project index registry."""
import json, subprocess
from pathlib import Path
from datetime import datetime

INDEX_PATH = Path("data/indexes/codemap_projects.json")

def load_index():
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text() or "{}")
    return {}

def save_index(data):
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(data, indent=2, default=str))

def get_project_info(project_path):
    idx = load_index()
    return idx.get(str(Path(project_path).resolve()))

def index_project(project_path, name=None, map_path=None, force=False):
    from sage.domains.codemap.codemap_scan import run_codemap_scan
    p = Path(project_path).resolve()
    key = str(p)
    idx = load_index()
    if not force and key in idx:
        return idx[key]
    if not map_path:
        safe = p.name.replace(" ","_").replace("/","_")
        map_path = Path(f"data/codemaps/{safe}_codemap.json")
    result = run_codemap_scan(p, map_path)
    head = ""
    try:
        r = subprocess.run(["git","rev-parse","HEAD"], capture_output=True, text=True, cwd=str(p), timeout=10)
        head = r.stdout.strip()
    except: pass
    info = {"project_path":key,"project_name":name or p.name,"map_path":str(map_path),"last_indexed_at":datetime.now().isoformat(),"git_head":head,"file_count":len(result.get("files",{})),"ops_count":result.get("ops_count",0)}
    idx[key] = info
    save_index(idx)
    return info

def list_projects():
    return list(load_index().values())
