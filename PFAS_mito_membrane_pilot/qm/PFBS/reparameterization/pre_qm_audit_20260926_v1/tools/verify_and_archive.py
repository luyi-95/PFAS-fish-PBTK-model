"""Verify immutable payload; write deterministic ZIP only outside package tree."""
import hashlib,json,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected={}
for line in (root/'SHA256SUMS').read_text().splitlines():
    h,n=line.split('  ',1);assert n not in expected;expected[n]=h
actual={p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file()}
assert set(actual)==set(expected)|{'SHA256SUMS'},'File-set mismatch'
for n,h in expected.items():assert sha(actual[n])==h,('Hash mismatch',n)
manifest=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
for n,h in manifest['payload_sha256'].items():assert sha(actual[n])==h,n
assert set(manifest['payload_sha256'])==set(actual)-{'SHA256SUMS','PACKAGE_MANIFEST.json'}
for n in actual:
    p=Path(n)
    assert '__pycache__' not in p.parts and p.suffix.lower() not in {'.pyc','.pyo','.chk','.fchk','.rwf','.int','.d2e','.tmp','.bak'},n
if len(sys.argv)>1:
    dest=Path(sys.argv[1]).resolve();assert not dest.is_relative_to(root),'Archive output must be external';assert not dest.exists(),'No overwrite'
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_STORED) as z:
        for n,p in sorted(actual.items()):
            info=zipfile.ZipInfo(n,date_time=(1980,1,1,0,0,0));info.create_system=3;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
    print(json.dumps({'status':'PASS','files':len(actual),'package_sha256':sha(dest),'archive_bytes':dest.stat().st_size}))
else:print(json.dumps({'status':'PASS','files':len(actual)}))
