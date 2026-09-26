"""Engine-free immutable package verification and deterministic archive reproduction."""
import hashlib,json,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={}
for line in (root/'SHA256SUMS').read_text().splitlines():
    h,n=line.split('  ',1)
    assert n not in expected and not Path(n).is_absolute() and '..' not in Path(n).parts,n
    expected[n]=h
actual={p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file()}
assert set(actual)==set(expected)|{'SHA256SUMS'},'File set mismatch'
for n,h in expected.items():assert sha(actual[n])==h,('Hash mismatch',n)
manifest=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
assert set(manifest['payload_sha256'])==set(actual)-{'SHA256SUMS','PACKAGE_MANIFEST.json'}
for n,h in manifest['payload_sha256'].items():assert sha(actual[n])==h,n
for n in actual:
    p=Path(n)
    assert '__pycache__' not in p.parts and '.git' not in p.parts,n
    assert p.suffix.lower() not in {'.pyc','.pyo','.chk','.fchk','.rwf','.int','.d2e','.tmp','.bak','.tpr','.trr','.xtc','.edr'},n
if len(sys.argv)>1:
    dest=Path(sys.argv[1]).resolve()
    assert not dest.is_relative_to(root) and not dest.exists(),'Output external and new only'
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_STORED) as z:
        for n,p in sorted(actual.items()):
            i=zipfile.ZipInfo(n,date_time=(1980,1,1,0,0,0));i.create_system=3;i.external_attr=0o100644<<16
            z.writestr(i,p.read_bytes())
    print(json.dumps({'status':'PASS','files':len(actual),'archive_bytes':dest.stat().st_size,'package_sha256':sha(dest)}))
else:print(json.dumps({'status':'PASS','files':len(actual)}))
