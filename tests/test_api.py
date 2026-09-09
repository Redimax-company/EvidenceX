import pathlib, tempfile, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
import backend.app as appmod

# Keep tests isolated from the user's demo database.
ROOT = pathlib.Path(tempfile.mkdtemp(prefix='evx-test-'))
appmod.DB = ROOT / 'evidence_x.db'
appmod.FILES = ROOT / 'files'
appmod.FILES.mkdir(parents=True, exist_ok=True)
appmod.init_db()
client = TestClient(appmod.app)

def h(u='investigator'): return {'X-User':u}

def test_login_role_and_health():
    r=client.get('/api/health'); assert r.status_code==200
    r=client.post('/api/login',json={'username':'investigator','password':'Investigator@123','role':'Investigator'}); assert r.status_code==200
    assert r.json()['role']=='Investigator'

def test_role_mismatch():
    r=client.post('/api/login',json={'username':'investigator','password':'Investigator@123','role':'Admin'}); assert r.status_code==403

def test_invalid_login():
    assert client.post('/api/login',json={'username':'investigator','password':'bad','role':'Investigator'}).status_code==401

def test_mfa_demo_code():
    r=client.get('/api/mfa/demo-code?action=DOCUMENT_UPLOAD',headers=h()); assert r.status_code==200; assert len(r.json()['code'])==6
