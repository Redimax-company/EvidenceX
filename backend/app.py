from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timezone
import sqlite3, hashlib, json, uuid, os, re, shutil, hmac, base64, struct, time, math, zipfile, io

BASE = Path(__file__).resolve().parent
DATA = BASE / 'data'
FILES = DATA / 'files'
DB = DATA / 'evidence_x.db'
FRONTEND = BASE.parent / 'frontend'
FILES.mkdir(parents=True, exist_ok=True)

app = FastAPI(title='EVIDENCE-X SIH26190', version='2.0.0')
app.mount('/static', StaticFiles(directory=FRONTEND), name='static')

USERS = {
    'admin': {'password':'Admin@123','role':'Admin','mfa_secret':'JBSWY3DPEHPK3PXP'},
    'investigator': {'password':'Investigator@123','role':'Investigator','mfa_secret':'KRSXG5A3NFXGOIDB'},
    'forensic': {'password':'Forensic@123','role':'Forensic Officer','mfa_secret':'MFRGGZDFMZTWQ2LK'},
    'legal': {'password':'Legal@123','role':'Legal Officer','mfa_secret':'ONSWG4TFOQXW4ZDF'},
    'auditor': {'password':'Auditor@123','role':'Auditor','mfa_secret':'K5XXE3DEOJSW4Y3P'},
}
ALL_ROLES = ['Admin','Investigator','Forensic Officer','Legal Officer','Auditor']
EDIT_ROLES = {'Admin','Investigator','Forensic Officer'}
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXT = {'.pdf','.docx','.txt','.jpg','.jpeg','.png'}
IMPORTANT_ACTIONS = {'DOCUMENT_UPLOAD','DOCUMENT_VERSION_CREATE','TAMPER_DEMO','VERSION_RESTORE','EVIDENCE_SEAL','LEGAL_HOLD','LEGAL_HOLD_RELEASE','DOCUMENT_DELETE'}

STOPWORDS=set('the and for with from this that into have has are was were you your document report case investigation evidence legal police court statement witness charge sheet forensic'.split())


def now(): return datetime.now(timezone.utc).isoformat()
def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c

def init_db():
    c=conn(); c.executescript('''
    CREATE TABLE IF NOT EXISTS documents(
      id TEXT PRIMARY KEY, case_id TEXT NOT NULL, title TEXT NOT NULL, doc_type TEXT NOT NULL,
      description TEXT, created_by TEXT NOT NULL, created_at TEXT NOT NULL, current_version INTEGER NOT NULL,
      allowed_roles TEXT NOT NULL, tamper_alert INTEGER NOT NULL DEFAULT 0,
      sealed INTEGER NOT NULL DEFAULT 0, sealed_version INTEGER, sealed_at TEXT, sealed_by TEXT,
      legal_hold INTEGER NOT NULL DEFAULT 0, legal_hold_reason TEXT, legal_hold_at TEXT, legal_hold_by TEXT,
      extracted_text TEXT DEFAULT '', ai_classification TEXT DEFAULT '', ai_confidence REAL DEFAULT 0,
      redaction_count INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS versions(
      id TEXT PRIMARY KEY, document_id TEXT NOT NULL, version INTEGER NOT NULL, sha256 TEXT NOT NULL,
      merkle_root TEXT, file_path TEXT NOT NULL, uploaded_by TEXT NOT NULL, uploaded_at TEXT NOT NULL,
      is_current INTEGER NOT NULL DEFAULT 0, sealed INTEGER NOT NULL DEFAULT 0,
      FOREIGN KEY(document_id) REFERENCES documents(id)
    );
    CREATE TABLE IF NOT EXISTS audit(
      id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, actor TEXT NOT NULL, role TEXT NOT NULL,
      action TEXT NOT NULL, document_id TEXT, case_id TEXT, details TEXT
    );
    CREATE TABLE IF NOT EXISTS blocks(
      block_no INTEGER PRIMARY KEY, transaction_id TEXT NOT NULL, timestamp TEXT NOT NULL,
      previous_hash TEXT NOT NULL, transactions TEXT NOT NULL, merkle_root TEXT NOT NULL, block_hash TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS mfa_challenges(
      id TEXT PRIMARY KEY, actor TEXT NOT NULL, action TEXT NOT NULL, created_at TEXT NOT NULL, used INTEGER NOT NULL DEFAULT 0
    );
    CREATE INDEX IF NOT EXISTS idx_docs_case ON documents(case_id);
    CREATE INDEX IF NOT EXISTS idx_docs_title ON documents(title);
    CREATE INDEX IF NOT EXISTS idx_docs_type ON documents(doc_type);
    CREATE INDEX IF NOT EXISTS idx_docs_hold ON documents(legal_hold);
    CREATE INDEX IF NOT EXISTS idx_docs_sealed ON documents(sealed);
    CREATE INDEX IF NOT EXISTS idx_versions_doc ON versions(document_id, version);
    CREATE INDEX IF NOT EXISTS idx_audit_time ON audit(timestamp DESC);
    CREATE VIRTUAL TABLE IF NOT EXISTS document_search USING fts5(document_id UNINDEXED, case_id, title, doc_type, created_by, content);
    CREATE TABLE IF NOT EXISTS redactions(
      id TEXT PRIMARY KEY, document_id TEXT NOT NULL, version INTEGER NOT NULL, created_by TEXT NOT NULL,
      created_at TEXT NOT NULL, redacted_path TEXT NOT NULL, findings TEXT NOT NULL
    );
    ''')
    # Migrate databases from v1.
    cols={r['name'] for r in c.execute('PRAGMA table_info(documents)')}
    additions={
      'sealed':'INTEGER NOT NULL DEFAULT 0','sealed_version':'INTEGER','sealed_at':'TEXT','sealed_by':'TEXT',
      'legal_hold':'INTEGER NOT NULL DEFAULT 0','legal_hold_reason':'TEXT','legal_hold_at':'TEXT','legal_hold_by':'TEXT',
      'extracted_text':"TEXT DEFAULT ''",'ai_classification':"TEXT DEFAULT ''",'ai_confidence':'REAL DEFAULT 0',
      'redaction_count':'INTEGER NOT NULL DEFAULT 0'}
    for name,typ in additions.items():
        if name not in cols: c.execute(f'ALTER TABLE documents ADD COLUMN {name} {typ}')
    vcols={r['name'] for r in c.execute('PRAGMA table_info(versions)')}
    if 'sealed' not in vcols: c.execute('ALTER TABLE versions ADD COLUMN sealed INTEGER NOT NULL DEFAULT 0')
    if c.execute('SELECT COUNT(*) FROM blocks').fetchone()[0] == 0:
        genesis={'block_no':0,'transaction_id':'GENESIS','timestamp':now(),'previous_hash':'GENESIS','transactions':'GENESIS','merkle_root':'GENESIS'}
        genesis['block_hash']=hashlib.sha256(json.dumps(genesis,sort_keys=True).encode()).hexdigest()
        c.execute('INSERT INTO blocks VALUES(?,?,?,?,?,?,?)',(0,genesis['transaction_id'],genesis['timestamp'],genesis['previous_hash'],genesis['transactions'],genesis['merkle_root'],genesis['block_hash']))
    c.commit(); c.close()
init_db()


def user_from_header(x_user):
    if not x_user or x_user not in USERS: raise HTTPException(401,'Invalid demo user')
    return x_user, USERS[x_user]['role']

def audit(actor, role, action, doc_id=None, case_id=None, details=''):
    c=conn(); c.execute('INSERT INTO audit VALUES(?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),now(),actor,role,action,doc_id,case_id,details)); c.commit(); c.close()

def get_doc(doc_id):
    c=conn(); r=c.execute('SELECT * FROM documents WHERE id=?',(doc_id,)).fetchone(); c.close()
    if not r: raise HTTPException(404,'Document not found')
    return r

def can_view(doc, role): return role=='Admin' or role in json.loads(doc['allowed_roles'])
def can_edit(doc, role, actor): return role=='Admin' or (role in EDIT_ROLES and role in json.loads(doc['allowed_roles'])) or actor==doc['created_by']

def require_doc(doc_id,user,write=False):
    actor,role=user; doc=get_doc(doc_id)
    if not can_view(doc,role):
        audit(actor,role,'ACCESS_DENIED',doc_id,doc['case_id'],'View permission denied'); raise HTTPException(403,'You do not have permission to access this document.')
    if write and not can_edit(doc,role,actor):
        audit(actor,role,'ACCESS_DENIED',doc_id,doc['case_id'],'Edit permission denied'); raise HTTPException(403,'You do not have permission to edit this document.')
    return doc

def check_modification_allowed(doc, action):
    if doc['legal_hold'] and action in {'DOCUMENT_VERSION_CREATE','TAMPER_DEMO','VERSION_RESTORE','DOCUMENT_DELETE'}:
        raise HTTPException(423,'Legal Hold is active. Modification or deletion is blocked.')

def sha_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()

def merkle_root(hashes):
    if not hashes: return hashlib.sha256(b'EMPTY').hexdigest()
    level=hashes[:]
    while len(level)>1:
        if len(level)%2: level.append(level[-1])
        level=[hashlib.sha256((level[i]+level[i+1]).encode()).hexdigest() for i in range(0,len(level),2)]
    return level[0]

def recalc_merkle():
    c=conn(); hs=[r['sha256'] for r in c.execute('SELECT sha256 FROM versions ORDER BY uploaded_at,id')]; c.close(); return merkle_root(hs)

def add_block(tx):
    c=conn(); last=c.execute('SELECT * FROM blocks ORDER BY block_no DESC LIMIT 1').fetchone(); no=last['block_no']+1; root=recalc_merkle(); ts=now(); txid=str(uuid.uuid4())
    payload={'block_no':no,'transaction_id':txid,'timestamp':ts,'previous_hash':last['block_hash'],'transactions':tx,'merkle_root':root}; bh=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    c.execute('INSERT INTO blocks VALUES(?,?,?,?,?,?,?)',(no,txid,ts,last['block_hash'],json.dumps(tx),root,bh)); c.commit(); c.close()
    return {'block_no':no,'transaction_id':txid,'block_hash':bh,'merkle_root':root}

def safe_name(name):
    ext=Path(name or '').suffix.lower()
    if ext not in ALLOWED_EXT: raise HTTPException(400,'Unsupported file type. Use PDF, DOCX, TXT, JPG or PNG.')
    stem=re.sub(r'[^A-Za-z0-9._-]','_',Path(name).stem)[:80]
    return (stem or 'document')+ext

def extract_text(filename, content):
    ext=Path(filename).suffix.lower()
    if ext=='.txt':
        return content.decode('utf-8','ignore')[:500000]
    if ext=='.docx':
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                xml=z.read('word/document.xml').decode('utf-8','ignore')
                return re.sub(r'<[^>]+>',' ',xml)[:500000]
        except Exception: return ''
    # Optional OCR: works when Pillow + Tesseract are installed. The core app remains runnable without them.
    if ext in {'.png','.jpg','.jpeg','.pdf'}:
        try:
            from PIL import Image
            import pytesseract
            if ext=='.pdf': return ''
            return pytesseract.image_to_string(Image.open(io.BytesIO(content)))[:500000]
        except Exception: return ''
    return ''

def classify_document(title, doc_type, text):
    s=(title+' '+doc_type+' '+text).lower()
    patterns=[
      ('FIR',['fir','first information report','complainant','police station']),
      ('Forensic Report',['forensic','laboratory','dna','fingerprint','forensic examination']),
      ('Witness Statement',['witness statement','deposition','statement of witness','eyewitness']),
      ('Charge Sheet',['charge sheet','chargesheet','accused','section 173']),
      ('Investigation Report',['investigation report','investigation findings','investigating officer']),
      ('Court Filing',['petition','court filing','before the hon','plaintiff','defendant']),
      ('Legal Notice',['legal notice','notice to','hereby called upon']),
      ('Judgment',['judgment','judgement','order of the court','disposed']),
      ('Evidence Record',['seized','seizure memo','evidence record','exhibit'])]
    best=('Unclassified',0)
    for label,words in patterns:
        score=sum(1 for w in words if w in s)
        if score>best[1]: best=(label,score)
    conf=min(0.99,0.55+best[1]*0.10) if best[1] else 0.20
    return best[0],round(conf,2)

def terms(text):
    return [w for w in re.findall(r'[a-z0-9]{3,}', text.lower()) if w not in STOPWORDS]

def semantic_rank(rows, query):
    q=set(terms(query)); scored=[]
    for r in rows:
        corpus=' '.join([r['case_id'],r['title'],r['doc_type'],r['created_by'],r['extracted_text'] or ''])
        ws=terms(corpus); vocab=set(ws); overlap=len(q & vocab); score=overlap/(math.sqrt(len(q)*len(vocab)) or 1)
        scored.append((score,r))
    return [dict(r,search_score=round(score,4)) for score,r in sorted(scored,key=lambda x:x[0],reverse=True) if score>0]

def totp(secret, for_time=None):
    key=base64.b32decode(secret + '='*((8-len(secret)%8)%8),casefold=True); counter=int((for_time or time.time())//30); msg=struct.pack('>Q',counter); digest=hmac.new(key,msg,hashlib.sha1).digest(); off=digest[-1]&15; code=(struct.unpack('>I',digest[off:off+4])[0]&0x7fffffff)%1000000; return f'{code:06d}'

class LoginIn(BaseModel): username:str; password:str; role:str
class MFAIn(BaseModel): action:str; document_id:str|None=None; code:str
class HoldIn(BaseModel): reason:str
class SealIn(BaseModel): version:int

@app.get('/')
def root(): return FileResponse(FRONTEND/'index.html')
@app.get('/api/health')
def health(): return {'status':'ok','service':'EVIDENCE-X','database':'sqlite','auth':'demo-header','mfa':'TOTP'}

@app.post('/api/login')
def login(body:LoginIn):
    u=USERS.get(body.username)
    if not u or u['password']!=body.password: raise HTTPException(401,'Invalid username or password.')
    if body.role!=u['role']: raise HTTPException(403,f'Role mismatch. {body.username} is registered as {u["role"]}.')
    audit(body.username,u['role'],'LOGIN',details='Demo login with role selection')
    return {'username':body.username,'role':u['role'],'mfa_enabled':True}

@app.get('/api/me')
def me(x_user:str=Header(None)): u,r=user_from_header(x_user); return {'username':u,'role':r,'mfa_enabled':True}

@app.get('/api/mfa/demo-code')
def mfa_demo_code(action:str='SENSITIVE_ACTION',x_user:str=Header(None)):
    actor,role=user_from_header(x_user); return {'action':action,'code':totp(USERS[actor]['mfa_secret']),'note':'Demo TOTP shown for SIH demonstration; production must use an authenticator app.'}

def verify_mfa(actor, action, code):
    if action not in IMPORTANT_ACTIONS: return
    expected=totp(USERS[actor]['mfa_secret'])
    if not hmac.compare_digest(str(code).strip(),expected): raise HTTPException(401,'MFA verification failed. Enter the current 6-digit TOTP.')

def rows_for_user(c, role):
    rows=c.execute('SELECT * FROM documents ORDER BY created_at DESC').fetchall(); return [r for r in rows if can_view(r,role)]

@app.get('/api/documents')
def documents(q:str='',case_id:str='',status:str='',semantic:bool=False,x_user:str=Header(None)):
    actor,role=user_from_header(x_user); c=conn(); rows=rows_for_user(c,role); c.close()
    if q:
        if semantic:
            rows=semantic_rank(rows,q)
        else:
            qq=q.lower(); rows=[dict(r) for r in rows if qq in ' '.join([r['id'],r['case_id'],r['title'],r['doc_type'],r['created_by'],r['extracted_text'] or '']).lower()]
    else: rows=[dict(r) for r in rows]
    if case_id: rows=[r for r in rows if r['case_id']==case_id]
    if status and status!='all': rows=[r for r in rows if ('tampered' if r['tamper_alert'] else 'authentic')==status]
    return rows

@app.post('/api/documents/upload')
async def upload(case_id:str=Form(...),title:str=Form(...),doc_type:str=Form(...),description:str=Form(''),allowed_roles:str=Form('[]'),mfa_code:str=Form(...),file:UploadFile=File(...),x_user:str=Header(None)):
    actor,role=user_from_header(x_user); verify_mfa(actor,'DOCUMENT_UPLOAD',mfa_code)
    if role not in {'Admin','Investigator','Forensic Officer'}: raise HTTPException(403,'Your role cannot upload documents.')
    try: roles=[r for r in json.loads(allowed_roles) if r in ALL_ROLES and r!='Admin']
    except: raise HTTPException(400,'Invalid access roles')
    if not roles: raise HTTPException(400,'Select at least one access role.')
    name=safe_name(file.filename); content=await file.read()
    if len(content)>MAX_FILE_SIZE: raise HTTPException(413,'File exceeds 50 MB demo limit.')
    did='DOC-'+uuid.uuid4().hex[:12].upper(); vid=str(uuid.uuid4()); folder=FILES/did; folder.mkdir(parents=True,exist_ok=True); path=folder/f'v1_{name}'; path.write_bytes(content)
    h=sha256_bytes(content); ts=now(); root=merkle_root([h]); text=extract_text(name,content); auto_type,conf=classify_document(title,doc_type,text)
    # Creator-selected type is retained; AI classification is stored separately.
    c=conn(); c.execute('INSERT INTO documents(id,case_id,title,doc_type,description,created_by,created_at,current_version,allowed_roles,tamper_alert,extracted_text,ai_classification,ai_confidence) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(did,case_id,title,doc_type,description,actor,ts,1,json.dumps(roles),0,text,auto_type,conf)); c.execute('INSERT INTO versions(id,document_id,version,sha256,merkle_root,file_path,uploaded_by,uploaded_at,is_current,sealed) VALUES(?,?,?,?,?,?,?,?,?,?)',(vid,did,1,h,root,str(path),actor,ts,1,0)); c.execute('INSERT INTO document_search(document_id,case_id,title,doc_type,created_by,content) VALUES(?,?,?,?,?,?)',(did,case_id,title,doc_type,actor,text)); c.commit(); c.close()
    audit(actor,role,'DOCUMENT_UPLOAD',did,case_id,f'Version 1 uploaded; SHA-256 {h}; AI classification={auto_type} ({conf:.0%})')
    block=add_block({'action':'DOCUMENT_UPLOAD','document_id':did,'case_id':case_id,'version':1,'sha256':h,'actor':actor})
    return {'document_id':did,'version':1,'sha256':h,'merkle_root':root,'ai_classification':auto_type,'ai_confidence':conf,'block':block}

@app.post('/api/documents/{doc_id}/versions')
async def new_version(doc_id:str,mfa_code:str=Form(...),file:UploadFile=File(...),x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user,write=True); check_modification_allowed(d,'DOCUMENT_VERSION_CREATE'); verify_mfa(user[0],'DOCUMENT_VERSION_CREATE',mfa_code)
    name=safe_name(file.filename); content=await file.read()
    if len(content)>MAX_FILE_SIZE: raise HTTPException(413,'File exceeds 50 MB demo limit.')
    c=conn(); latest=c.execute('SELECT MAX(version) n FROM versions WHERE document_id=?',(doc_id,)).fetchone()['n'] or 0; ver=latest+1; c.execute('UPDATE versions SET is_current=0 WHERE document_id=?',(doc_id,))
    vid=str(uuid.uuid4()); ts=now(); h=sha256_bytes(content); folder=FILES/doc_id; folder.mkdir(parents=True,exist_ok=True); path=folder/f'v{ver}_{name}'; path.write_bytes(content); root=merkle_root([r['sha256'] for r in c.execute('SELECT sha256 FROM versions ORDER BY uploaded_at,id')]+[h]); text=extract_text(name,content); auto_type,conf=classify_document(d['title'],d['doc_type'],text)
    c.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?,?,?,?)',(vid,doc_id,ver,h,root,str(path),user[0],ts,1,0)); c.execute('UPDATE documents SET current_version=?,tamper_alert=0,extracted_text=?,ai_classification=?,ai_confidence=? WHERE id=?',(ver,text,auto_type,conf,doc_id)); c.commit(); c.close()
    audit(user[0],user[1],'DOCUMENT_VERSION_CREATE',doc_id,d['case_id'],f'Version {ver} created; SHA-256 {h}; AI classification={auto_type}')
    block=add_block({'action':'DOCUMENT_VERSION_CREATE','document_id':doc_id,'case_id':d['case_id'],'version':ver,'sha256':h,'actor':user[0]})
    return {'document_id':doc_id,'version':ver,'sha256':h,'merkle_root':root,'ai_classification':auto_type,'ai_confidence':conf,'block':block}

@app.get('/api/documents/{doc_id}')
def detail(doc_id:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user); c=conn(); vs=c.execute('SELECT * FROM versions WHERE document_id=? ORDER BY version DESC',(doc_id,)).fetchall(); reds=c.execute('SELECT * FROM redactions WHERE document_id=? ORDER BY created_at DESC',(doc_id,)).fetchall(); c.close()
    return {'document':dict(d),'versions':[dict(v) for v in vs],'redactions':[dict(r) for r in reds]}

@app.get('/api/documents/{doc_id}/download')
def download(doc_id:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user); c=conn(); v=c.execute('SELECT * FROM versions WHERE document_id=? AND version=?',(doc_id,d['current_version'],)).fetchone(); c.close(); audit(user[0],user[1],'DOCUMENT_DOWNLOAD',doc_id,d['case_id'],f'Version {d["current_version"]}'); return FileResponse(v['file_path'],filename=Path(v['file_path']).name)

@app.get('/api/documents/{doc_id}/verify')
def verify(doc_id:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user); c=conn(); v=c.execute('SELECT * FROM versions WHERE document_id=? AND version=?',(doc_id,d['current_version'])).fetchone(); c.close(); actual=sha_file(v['file_path']); authentic=actual==v['sha256']; audit(user[0],user[1],'INTEGRITY_VERIFY',doc_id,d['case_id'],f'Version {v["version"]}: {"AUTHENTIC" if authentic else "TAMPERED"}')
    if not authentic:
        c=conn(); c.execute('UPDATE documents SET tamper_alert=1 WHERE id=?',(doc_id,)); c.commit(); c.close()
    return {'document_id':doc_id,'version':v['version'],'expected_hash':v['sha256'],'actual_hash':actual,'status':'AUTHENTIC' if authentic else 'TAMPERED','alert':not authentic,'sealed':bool(v['sealed'])}

@app.post('/api/documents/{doc_id}/tamper-demo')
def tamper(doc_id:str,mfa_code:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user,write=True); check_modification_allowed(d,'TAMPER_DEMO'); verify_mfa(user[0],'TAMPER_DEMO',mfa_code)
    c=conn(); v=c.execute('SELECT * FROM versions WHERE document_id=? AND version=?',(doc_id,d['current_version'],)).fetchone(); c.close()
    if v['sealed']: raise HTTPException(423,'This evidence version is permanently sealed and cannot be modified.')
    p=Path(v['file_path']); original=p.read_bytes(); p.write_bytes(original+b'\nEVIDENCE-X DEMO TAMPER MARKER - UNAUTHORIZED CHANGE\n')
    audit(user[0],user[1],'TAMPER_DEMO',doc_id,d['case_id'],f'Physical demo mutation of Version {v["version"]}; anchored hash retained'); c=conn(); c.execute('UPDATE documents SET tamper_alert=1 WHERE id=?',(doc_id,)); c.commit(); c.close(); add_block({'action':'TAMPER_DEMO','document_id':doc_id,'case_id':d['case_id'],'version':v['version'],'actor':user[0],'note':'Anchored hash intentionally unchanged'}); return {'status':'TAMPER_INJECTED','document_id':doc_id,'version':v['version']}

@app.post('/api/documents/{doc_id}/restore/{version}')
def restore(doc_id:str,version:int,mfa_code:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user,write=True); check_modification_allowed(d,'VERSION_RESTORE'); verify_mfa(user[0],'VERSION_RESTORE',mfa_code); c=conn(); v=c.execute('SELECT * FROM versions WHERE document_id=? AND version=?',(doc_id,version)).fetchone()
    if not v: c.close(); raise HTTPException(404,'Version not found')
    if v['sealed'] is False and sha_file(v['file_path'])!=v['sha256']: c.close(); raise HTTPException(409,'Selected version is tampered and cannot be restored.')
    current=c.execute('SELECT * FROM versions WHERE document_id=? AND version=?',(doc_id,d['current_version'],)).fetchone(); c.execute('UPDATE versions SET is_current=0 WHERE document_id=?',(doc_id,)); c.execute('UPDATE versions SET is_current=1 WHERE id=?',(v['id'],)); c.execute('UPDATE documents SET current_version=?,tamper_alert=0 WHERE id=?',(version,doc_id)); c.commit(); c.close(); audit(user[0],user[1],'VERSION_RESTORE',doc_id,d['case_id'],f'Restored Version {version}; prior current Version {current["version"] if current else "-"} retained'); add_block({'action':'VERSION_RESTORE','document_id':doc_id,'case_id':d['case_id'],'version':version,'actor':user[0]}); return {'status':'RESTORED','version':version}

@app.post('/api/documents/{doc_id}/seal')
def seal(doc_id:str,body:SealIn,mfa_code:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user,write=True); verify_mfa(user[0],'EVIDENCE_SEAL',mfa_code); c=conn(); v=c.execute('SELECT * FROM versions WHERE document_id=? AND version=?',(doc_id,body.version)).fetchone()
    if not v: c.close(); raise HTTPException(404,'Version not found')
    if sha_file(v['file_path'])!=v['sha256']: c.close(); raise HTTPException(409,'Cannot seal a tampered version.')
    ts=now(); c.execute('UPDATE versions SET sealed=1 WHERE id=?',(v['id'],)); c.execute('UPDATE documents SET sealed=1,sealed_version=?,sealed_at=?,sealed_by=? WHERE id=?',(body.version,ts,user[0],doc_id)); c.commit(); c.close(); audit(user[0],user[1],'EVIDENCE_SEAL',doc_id,d['case_id'],f'Version {body.version} permanently sealed'); add_block({'action':'EVIDENCE_SEAL','document_id':doc_id,'version':body.version,'actor':user[0]}); return {'status':'SEALED','version':body.version}

@app.post('/api/documents/{doc_id}/legal-hold')
def legal_hold(doc_id:str,body:HoldIn,mfa_code:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user,write=True); 
    if user[1] not in {'Admin','Legal Officer'}: raise HTTPException(403,'Only Admin or Legal Officer can place a Legal Hold.')
    verify_mfa(user[0],'LEGAL_HOLD',mfa_code); ts=now(); c=conn(); c.execute('UPDATE documents SET legal_hold=1,legal_hold_reason=?,legal_hold_at=?,legal_hold_by=? WHERE id=?',(body.reason,ts,user[0],doc_id)); c.commit(); c.close(); audit(user[0],user[1],'LEGAL_HOLD',doc_id,d['case_id'],body.reason); add_block({'action':'LEGAL_HOLD','document_id':doc_id,'actor':user[0],'reason':body.reason}); return {'status':'LEGAL_HOLD_ACTIVE'}

@app.delete('/api/documents/{doc_id}')
def delete_doc(doc_id:str,mfa_code:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user,write=True)
    if user[1]!='Admin': raise HTTPException(403,'Only Admin can delete documents.')
    if d['legal_hold']: raise HTTPException(423,'Legal Hold is active. Deletion is blocked.')
    verify_mfa(user[0],'DOCUMENT_DELETE',mfa_code); c=conn(); vs=c.execute('SELECT file_path FROM versions WHERE document_id=?',(doc_id,)).fetchall(); c.execute('DELETE FROM versions WHERE document_id=?',(doc_id,)); c.execute('DELETE FROM documents WHERE id=?',(doc_id,)); c.execute('DELETE FROM document_search WHERE document_id=?',(doc_id,)); c.commit(); c.close(); shutil.rmtree(FILES/doc_id,ignore_errors=True); audit(user[0],user[1],'DOCUMENT_DELETE',doc_id,d['case_id'],'Document deleted'); return {'status':'DELETED'}

@app.post('/api/documents/{doc_id}/redact')
def redact(doc_id:str,mfa_code:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user); verify_mfa(user[0],'DOCUMENT_VERSION_CREATE',mfa_code); c=conn(); v=c.execute('SELECT * FROM versions WHERE document_id=? AND version=?',(doc_id,d['current_version'])).fetchone(); c.close(); src=Path(v['file_path']); raw=src.read_bytes(); text=d['extracted_text'] or ''
    findings=[]
    patterns=[('Aadhaar',r'\b\d{4}[ -]?\d{4}[ -]?\d{4}\b'),('Phone',r'\b(?:\+91[- ]?)?[6-9]\d{9}\b'),('Email',r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')]
    red_text=text
    for label,pat in patterns:
        matches=list(re.finditer(pat,red_text)); findings += [{'type':label,'match':'[REDACTED]'} for _ in matches]; red_text=re.sub(pat,'[REDACTED]',red_text)
    # Text/DOCX redacted copy is content-preserving for the demo. Binary images/PDFs get a sidecar .redacted.txt representation when OCR text exists.
    out=FILES/doc_id/f'redacted_v{v["version"]}.txt'; out.write_text(red_text if red_text else 'No extractable text. Original evidence is unchanged.\nDetected sensitive-data count: '+str(len(findings)),encoding='utf-8')
    rid=str(uuid.uuid4()); ts=now(); c=conn(); c.execute('INSERT INTO redactions VALUES(?,?,?,?,?,?,?)',(rid,doc_id,v['version'],user[0],ts,str(out),json.dumps(findings))); c.execute('UPDATE documents SET redaction_count=redaction_count+1 WHERE id=?',(doc_id,)); c.commit(); c.close(); audit(user[0],user[1],'SENSITIVE_DATA_REDACTION',doc_id,d['case_id'],f'{len(findings)} findings; original version unchanged'); return {'status':'REDACTED_COPY_CREATED','count':len(findings),'path':str(out),'findings':findings}

@app.get('/api/documents/{doc_id}/redacted')
def redacted(doc_id:str,x_user:str=Header(None)):
    user=user_from_header(x_user); d=require_doc(doc_id,user); c=conn(); r=c.execute('SELECT * FROM redactions WHERE document_id=? ORDER BY created_at DESC LIMIT 1',(doc_id,)).fetchone(); c.close()
    if not r: raise HTTPException(404,'No redacted copy exists yet.')
    return FileResponse(r['redacted_path'],filename='redacted_copy.txt')

@app.get('/api/audit')
def get_audit(x_user:str=Header(None)):
    actor,role=user_from_header(x_user); c=conn(); rows=c.execute('SELECT * FROM audit ORDER BY timestamp DESC LIMIT 500').fetchall() if role in {'Admin','Auditor'} else c.execute('SELECT * FROM audit WHERE actor=? ORDER BY timestamp DESC LIMIT 200',(actor,)).fetchall(); c.close(); return [dict(r) for r in rows]

@app.get('/api/blockchain')
def blockchain(x_user:str=Header(None)):
    actor,role=user_from_header(x_user); 
    if role not in ALL_ROLES: raise HTTPException(403,'Ledger access denied')
    c=conn(); rows=c.execute('SELECT * FROM blocks ORDER BY block_no DESC').fetchall(); c.close(); return [dict(r) for r in rows]

@app.get('/api/stats')
def stats(x_user:str=Header(None)):
    actor,role=user_from_header(x_user); c=conn(); docs=c.execute('SELECT * FROM documents').fetchall(); accessible=[d for d in docs if can_view(d,role)]; versions=c.execute('SELECT COUNT(*) n FROM versions').fetchone()['n']; audits=c.execute('SELECT COUNT(*) n FROM audit').fetchone()['n']; blocks=c.execute('SELECT COUNT(*) n FROM blocks').fetchone()['n']; tampered=sum(d['tamper_alert'] for d in accessible); holds=sum(d['legal_hold'] for d in accessible); sealed=sum(d['sealed'] for d in accessible); c.close(); return {'documents':len(docs),'accessible_documents':len(accessible),'versions':versions,'audit_events':audits,'verified_documents':max(0,len(accessible)-tampered),'tampered_documents':tampered,'blockchain_transactions':max(0,blocks-1),'legal_hold_documents':holds,'sealed_documents':sealed}
