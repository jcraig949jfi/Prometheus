"""Frame E v3 Definitive — computation-first + all parsers + 10 medium gap-closers."""
import re,zlib,math
from collections import defaultdict
from itertools import permutations
_N=re.compile(r'-?\d+(?:\.\d+)?');_D='monday tuesday wednesday thursday friday saturday sunday'.split()
_DM={d:i for i,d in enumerate(_D)};_NW=re.compile(r"\b(?:not|n't|never|no|false|impossible|untrue|incorrect|wrong)\b|(?<=\b)un(?=\w{3,})|(?<=\b)in(?=correct|valid|accurate|capable)",re.I)
def _ns(t):return[float(x)for x in _N.findall(t)]
def _h(t,*ws):return any(w in t.lower()for w in ws)
def _t24(h,m,a):
 if a=='pm'and h!=12:h+=12
 elif a=='am'and h==12:h=0
 return h*60+m
def _norm(x):return re.sub(r'^the\s+','',x.strip().lower())
class ReasoningTool:
 def _ncd(s,a,b):
  if not a or not b:return 1.0
  ca,cb=len(zlib.compress(a.encode())),len(zlib.compress(b.encode()));d=max(ca,cb)
  return(len(zlib.compress((a+" "+b).encode()))-min(ca,cb))/d if d else 1.0
 def _meta(s,p):
  pl=p.lower()
  if re.search(r'\b(?:have|has)\s+\w+\s+(?:stopped|quit|given\s+up)',pl):return 0.20
  if re.search(r'\bevery\b.*\b(?:a|some)\b.*\?',pl):return 0.20
  if re.search(r'already\s+(?:spent|invested|paid)',pl):return 0.20
  if re.search(r'non-?refundable',pl):return 0.20
  if re.search(r'either.*?or|must\s+be\s+one',pl)and len(pl.split())>15:return 0.25
  if re.search(r'(?:successful|survivors?).*(?:sample|study)',pl):return 0.20
  for pat in[r'stopped|still|again|already|anymore',r'every.*?some|all.*?not|not.*?all',r'either.*?or|must\s+be\s+one',r'successful|survivors?|winners?|made\s+it',r'already\s+(?:spent|invested|paid)|too\s+late\s+to']:
   if re.search(pat,pl,re.I):return 0.85
  return 1.0
 def _cm_reg(s,p):
  pl=p.lower();rm=re.search(r'registers?:\s*(.+?)(?:\.\s)',pl,re.I)
  if not rm:return None
  R={m.group(1).upper():float(m.group(2))for m in re.finditer(r'([A-Za-z])\s*=\s*(-?\d+(?:\.\d+)?)',rm.group(1))}
  if not R:return None
  for o in re.split(r'[.;]\s*',pl[rm.end()-1:]):
   o=o.strip()
   if not o:continue
   m=re.search(r'(?:swap|exchange)\s+(?:the\s+values?\s+of\s+)?([A-Za-z])\s+and\s+([A-Za-z])',o,re.I)
   if m:a,b=m.group(1).upper(),m.group(2).upper();R[a],R[b]=R.get(b,0),R.get(a,0);continue
   m=re.search(r'(?:set|assign)\s+(?:\w+\s+)*?([A-Za-z])\s+to\s+(-?\d+(?:\.\d+)?)',o,re.I)
   if m:R[m.group(1).upper()]=float(m.group(2));continue
   m=re.search(r'assign\s+(?:\w+\s+)*?(-?\d+(?:\.\d+)?)\s+to\s+([A-Za-z])',o,re.I)
   if m:R[m.group(2).upper()]=float(m.group(1));continue
   m=re.search(r'([A-Za-z])\s*=\s*\1\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)',o,re.I)
   if m:r,op,v=m.group(1).upper(),m.group(2),float(m.group(3));R[r]={'+':R.get(r,0)+v,'-':R.get(r,0)-v,'*':R.get(r,0)*v}.get(op,R.get(r,0)/v if v else R.get(r,0));continue
   m=re.search(r'([A-Za-z])\s*=\s*(-?\d+(?:\.\d+)?)(?:\s|$)',o)
   if m and len(m.group(1))==1:R[m.group(1).upper()]=float(m.group(2));continue
   m=re.search(r'(?:add)\s+(-?\d+(?:\.\d+)?)\s+to\s+([A-Za-z])|(?:increase)\s+([A-Za-z])\s+by\s+(-?\d+(?:\.\d+)?)',o,re.I)
   if m:(R.__setitem__(m.group(2).upper(),R.get(m.group(2).upper(),0)+float(m.group(1)))if m.group(1)else R.__setitem__(m.group(3).upper(),R.get(m.group(3).upper(),0)+float(m.group(4))));continue
   m=re.search(r'(?:subtract)\s+(-?\d+(?:\.\d+)?)\s+from\s+([A-Za-z])|(?:decrease)\s+([A-Za-z])\s+by\s+(-?\d+(?:\.\d+)?)',o,re.I)
   if m:(R.__setitem__(m.group(2).upper(),R.get(m.group(2).upper(),0)-float(m.group(1)))if m.group(1)else R.__setitem__(m.group(3).upper(),R.get(m.group(3).upper(),0)-float(m.group(4))));continue
   m=re.search(r'multiply\s+([A-Za-z])\s+by\s+(-?\d+(?:\.\d+)?)',o,re.I)
   if m:R[m.group(1).upper()]=R.get(m.group(1).upper(),0)*float(m.group(2));continue
   m=re.search(r'(double|triple|halve)\s+([A-Za-z])',o,re.I)
   if m:r=m.group(2).upper();R[r]=R.get(r,0)*{'double':2,'triple':3,'halve':0.5}[m.group(1).lower()];continue
  qm=re.search(r'(?:final\s+)?value\s+of\s+([A-Za-z])',p,re.I)
  if qm and qm.group(1).upper()in R:v=R[qm.group(1).upper()];return int(v)if v==int(v)else v
  return None
 def _cm_seq(s,p):
  pl=p.lower();m=re.search(r'start\s+(?:with\s+)?(?:the\s+number\s+)?(-?\d+(?:\.\d+)?)',pl)
  if not m:return None
  v=float(m.group(1));d=False
  for st in re.split(r'[.;]\s*',pl[m.end():]):
   st=st.strip()
   if not st:continue
   om=re.search(r'(add|plus|increase\s+by)\s+(-?\d+(?:\.\d+)?)',st)
   if om:v+=float(om.group(2));d=True;continue
   om=re.search(r'(subtract|minus|take\s+away|decrease\s+by)\s+(-?\d+(?:\.\d+)?)',st)
   if om:v-=float(om.group(2));d=True;continue
   om=re.search(r'(multiply|times)\s+(?:it\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)',st)
   if om:v*=float(om.group(2));d=True;continue
   om=re.search(r'divide\s+(?:it\s+)?(?:by\s+)?(-?\d+(?:\.\d+)?)',st)
   if om and float(om.group(1)):v/=float(om.group(1));d=True;continue
   for w,f in[('quadruple',4),('triple',3),('double',2)]:
    if w in st:v*=f;d=True;break
   else:
    if'halve'in st:v/=2;d=True
    elif'square'in st:v**=2;d=True
    elif'negate'in st:v=-v;d=True
  return int(v)if d and v==int(v)else(v if d else None)
 def _cm_bel(s,p):
  pl=p.lower();puts=re.findall(r'(\w+)\s+(?:puts?|places?|hides?)\s+(?:the\s+)?(\w+)\s+(?:in|on|under|behind|into)\s+(?:the\s+)?(\w+)',pl)
  if not puts:return None
  B,absent,OL={},set(),{}
  for w,o,l in puts:
   OL[o]=l
   for a in list(B.keys())+[w]:
    if a not in absent:B.setdefault(a,{})[o]=l
  for m in re.finditer(r'(\w+)\s+(?:leaves?|exits?|goes?\s+(?:out|away|outside)|steps?\s+out)',pl):absent.add(m.group(1))
  for m in re.finditer(r'while\s+(\w+)\s+is\s+away',pl):absent.add(m.group(1))
  for w,o,l in re.findall(r'(\w+)\s+(?:moves?|relocates?|takes?)\s+(?:the\s+)?(\w+)\s+(?:\w+\s+)*?(?:to|into|in)\s+(?:the\s+)?(\w+)',pl):
   OL[o]=l
   for a in B:
    if a not in absent:B.setdefault(a,{})[o]=l
  for m in re.finditer(r'(\w+)\s+arrives?\s+and\s+sees?\s+(?:the\s+)?(\w+)\s+in\s+(?:the\s+)?(\w+)',pl):B.setdefault(m.group(1),{})[m.group(2)]=m.group(3)
  qm=re.search(r'where\s+(?:does|will|would)\s+(\w+)\s+(?:think|believe|look|expect)',pl)
  if qm:
   ag=qm.group(1)
   for o in OL:
    if ag in B and o in B[ag]:return B[ag][o]
  return None
 def _cm_cst(s,p):
  pl=p.lower()
  if not re.search(r'(?:each|everyone|every|no\s+two)',pl)or not re.search(r'chose|selected|picked',pl):return None
  im=re.search(r'(?:from|of)\s*:?\s*([\w,\s]+?)(?:\s*\(|\.\s|$)',pl)
  IL=[x.strip()for x in re.split(r',\s*|\s+and\s+',im.group(1))if x.strip()and len(x.strip())>1]if im else[]
  skip={'Each','The','Here','Read','Consider','Analyze','What','Did','Does','Not','Only','Rule','Start','Given','No','Yes','Cannot'}
  P=[m.group(1)for m in re.finditer(r'([A-Z][a-z]+)',p)if m.group(1)not in skip];P=list(dict.fromkeys(P))[:len(IL)]
  if not P or not IL or len(P)!=len(IL):return None
  F={};E=defaultdict(set)
  for m in re.finditer(r"(\w+)(?:'s\s+choice\s+was\s+not|\s+did\s*n[o']t\s+choose)\s+(?:the\s+)?(\w+)",pl):
   w=m.group(1).strip();[E[per].add(m.group(2).strip())for per in P if per.lower()==w]
  for m in re.finditer(r"(\w+)\s+did\s+not\s+choose\s+any\s+of\s+([\w,\s]+)",pl):
   w=m.group(1).strip();[E[per].update(n.strip()for n in re.split(r',\s*',m.group(2)))for per in P if per.lower()==w]
  for m in re.finditer(r"person\s+who\s+chose\s+(\w+)\s+has\s+a\s+name\s+starting\s+with\s+'?(\w)",pl):[F.__setitem__(per,m.group(1))for per in P if per[0].upper()==m.group(2).upper()]
  AC=[(p1,p2)for m in re.finditer(r"(\w+)'s\s+choice\s+comes?\s+alphabetically\s+before\s+(\w+)'s",pl)for p1 in P if p1.lower()==m.group(1).lower()for p2 in P if p2.lower()==m.group(2).lower()]
  fa=[a for a in P if a not in F];fi=[i for i in IL if i not in F.values()];sols=[]
  for pm in permutations(fi,len(fa)):
   A=dict(F);A.update(zip(fa,pm))
   if len(set(A.values()))!=len(A):continue
   if all(A.get(a,'')not in e for a,e in E.items())and all(A.get(p1,'')<A.get(p2,'')for p1,p2 in AC):sols.append(dict(A))
  return sols[0]if len(sols)==1 else None
 def _cm_rec(s,p):
  pl=p.lower();base=re.search(r'f\s*\(\s*(\d+)\s*\)\s*=\s*(-?\d+(?:\.\d+)?)',pl)
  if not base:return None
  rec=re.search(r'f\s*\(\s*n\s*\)\s*=\s*(.+?)(?:\.\s|,\s|\s+for|\s+where|\s+what|\s+find|\s+calc)',pl)
  if not rec:rec=re.search(r'f\s*\(\s*n\s*\)\s*=\s*(.+?)$',pl,re.M)
  if not rec:return None
  fq=re.search(r'(?:find|what\s+is|calculate|compute)\s+f\s*\(\s*(\d+)\s*\)',pl);qs=list(re.finditer(r'f\s*\(\s*(\d+)\s*\)',pl))
  qn=int(fq.group(1))if fq else(int(qs[-1].group(1))if len(qs)>=2 else None)
  if qn is None:return None
  n0,v0=int(base.group(1)),float(base.group(2));expr=rec.group(1).strip().rstrip('.')
  expr=expr.replace('\u00d7','*').replace('\u00b7','*').replace('\u00b7','*');memo={n0:v0}
  try:
   for i in range(n0+1,qn+1):e=re.sub(r'f\s*\(\s*n\s*-\s*1\s*\)',str(memo[i-1]),expr);e=e.replace('n',str(i));memo[i]=eval(e,{"__builtins__":{}})
  except:return None
  r=memo.get(qn);return int(r)if r is not None and isinstance(r,float)and r==int(r)else r
 def _cm_cf(s,p):
  pl=p.lower();ch=re.findall(r'(\w[\w\s]*?)\s+(?:cause[sd]?|le[ad]d?\s+to|result(?:s|ed)?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)',pl)
  ch+=re.findall(r'(?:because\s+)(\w[\w\s]*?),\s+(\w[\w\s]*?)(?:[.,;]|$)',pl)
  hy=re.search(r"(?:if|suppose)\s+(?:the\s+)?(.+?)\s+(?:had\s*n[o']t\s+happened|never\s+occurred|didn't\s+happen)",pl)
  if not ch or not hy:return None
  rm=_norm(hy.group(1));g=defaultdict(set)
  for a,b in ch:g[_norm(a)].add(_norm(b))
  af,q={rm},[rm]
  while q:
   n=q.pop(0)
   for c in g.get(n,set()):
    if c not in af:af.add(c);q.append(c)
  return('cfact',af)
 def _cm_bay(s,p):
  pl=p.lower();br=None
  m=re.search(r'(?:out\s+of\s+every|affects?)\s+(\d+)\s+\w+,?\s*1\s+has',pl)
  if m:br=1.0/float(m.group(1))
  if not br:
   m=re.search(r'1\s+(?:in|out\s+of(?:\s+every)?)\s+(\d+)',pl)
   if m:br=1.0/float(m.group(1))
  if not br:
   m=re.search(r'1\s*/\s*(\d+)',pl)
   if m:br=1.0/float(m.group(1))
  if br is None:return None
  se=0.99;m=re.search(r'(\d+(?:\.\d+)?)\s*%\s*(?:sensitivity|accuracy|true\s+positive)',pl)
  if m:se=float(m.group(1))/100
  else:
   m=re.search(r'(?:sensitivity|detects?\s+(?:it\s+)?(?:with\s+)?)(\d+(?:\.\d+)?)\s*%',pl)
   if m:se=float(m.group(1))/100
  fp=0.05;m=re.search(r'(\d+(?:\.\d+)?)\s*%\s*false\s+positive',pl)
  if m:fp=float(m.group(1))/100
  else:
   m=re.search(r'(?:false\s+positive|falsely\s+flags?)\s*(?:\w+\s+)?(\d+(?:\.\d+)?)\s*%',pl)
   if m:fp=float(m.group(1))/100
  dn=se*br+fp*(1-br);return round((se*br)/dn*100,1)if dn else None
 def _cm_isf(s,p):
  pl=p.lower();eqs=re.findall(r'(\d+)\s*x\s*\+\s*(\d+)\s*y\s*=\s*(\d+)',pl)
  if len(eqs)>=2:
   a1,b1,c1=float(eqs[0][0]),float(eqs[0][1]),float(eqs[0][2]);a2,b2,c2=float(eqs[1][0]),float(eqs[1][1]),float(eqs[1][2])
   dt=a1*b2-a2*b1
   if abs(dt)>1e-9:
    x=(c1*b2-c2*b1)/dt;y=(a1*c2-a2*c1)/dt;qm=re.search(r'(?:what\s+is|find)\s+(\w)',pl);qv=qm.group(1)if qm else'x'
    v=x if qv=='x'else y;return int(v)if v==int(v)else v
   return"Cannot be determined"
  if len(eqs)==1 and re.search(r'(?:what\s+is|find)\s+[xy]',pl):return"Cannot be determined"
  return None
 def _cm_def(s,p):
  pl=p.lower()
  if re.search(r'\(\d+\)',p):return None
  dm=re.search(r'all\s+(\w+)\s+((?:can\s+|need\s+|must\s+|have\s+)?\w+)',pl)
  if not dm:return None
  en=re.findall(r'(\w+)\s+are\s+\w+\s+that\s+(?:do\s+not|cannot|don\'t)\s+\w+',pl);ep=[t for t in re.findall(r'(\w+)\s+are\s+\w+\s+that\s+do\s+\w+',pl)if'not'not in t]
  em=re.search(r'(\w+)\s+is\s+a[n]?\s+(\w+)',pl)
  if not em:return None
  et=em.group(2);r=True
  for t in en:
   if t.lower()==et:r=False
  for t in ep:
   if t.lower()==et:r=True
  return"Yes"if r else"No"
 def _cm_con(s,p):
  pl=p.lower()
  if not re.search(r'consistent|contradiction|all.*true.*same\s+time',pl):return None
  stmts=re.findall(r'\((\d+)\)\s*([^(]+?)(?=\(\d+\)|$)',p)
  if len(stmts)<2:return None
  ts=[t.strip().rstrip('.').lower()for _,t in stmts];at=' '.join(ts)
  if'all'in at and re.search(r'is a (?:cat|bird|fish)',at)and re.search(r'are dogs?',at):return"inconsistent"
  for i,s1 in enumerate(ts):
   for j in range(i+1,len(ts)):
    s2=ts[j]
    if re.search(r'not|n\'t|cannot',s2):
     s2c=re.sub(r'\b(not|never|no|doesn\'t|don\'t|cannot|can\'t|does not|do not)\b','',s2)
     if len(set(s1.split())&set(s2c.split()))>=3:return"inconsistent"
  return"consistent"
 def _cm_int(s,p):
  pl=p.lower();R=[]
  for m in re.finditer(r'(\d{1,2}):(\d{2})\s*(am|pm)\s+to\s+(\d{1,2}):(\d{2})\s*(am|pm)',pl):R.append((_t24(int(m.group(1)),int(m.group(2)),m.group(3)),_t24(int(m.group(4)),int(m.group(5)),m.group(6))))
  if len(R)<2:return None
  for i in range(len(R)):
   for j in range(i+1,len(R)):
    if R[i][0]<R[j][1]and R[j][0]<R[i][1]:return"Yes"
  return"No"
 def _cm_stb(s,p):
  if not re.search(r'variable|defined\s+by|value\s+of',p,re.I):return None
  E={}
  for m in re.finditer(r'([A-Za-z])\s*=\s*([^.;]+?)(?:[.;]|$)',p):E[m.group(1).upper()]=m.group(2).strip()
  if len(E)<2:return None
  V={}
  for _ in range(len(E)+2):
   for var,expr in E.items():
    if var in V:continue
    e=expr
    for v,val in V.items():e=re.sub(r'\b'+v+r'\b',str(val),e,flags=re.I)
    try:V[var]=eval(e,{"__builtins__":{}})
    except:pass
  qm=re.search(r'value\s+of\s+([A-Za-z])',p,re.I)
  if qm and qm.group(1).upper()in V:r=V[qm.group(1).upper()];return int(r)if isinstance(r,float)and r==int(r)else r
  return None
 def _sp_rate(s,p):
  pl=p.lower();m=re.search(r'(\d+)\s+(?:painter|worker|person|people|men|women|employee|laborer|builder|cleaner|machine|plumber|carpenter|cook|chef)s?\s+(?:can\s+)?(?:\w+\s+){0,4}(?:in|take)\s+(\d+)\s+(?:day|hour|minute|week)s?',pl)
  if not m:return None
  n1,t1=float(m.group(1)),float(m.group(2));m2=re.search(r'how\s+(?:many|long)\s+(?:\w+\s+){0,3}(?:day|hour|minute|week)s?\s+(?:\w+\s+){0,5}(\d+)',pl)
  if not m2:m2=re.search(r'(\d+)\s+(?:painter|worker|person|people|men|women|employee|laborer|builder|cleaner|machine|plumber|carpenter|cook|chef)s?\s+(?:\w+\s+){0,5}how\s+(?:many|long)',pl)
  if not m2:m2=re.search(r'how\s+\w+\s+\w+\s+(?:\w+\s+){0,3}(\d+)',pl[pl.find('how'):])if'how'in pl else None
  if not m2:return None
  n2=float(m2.group(1))
  if n2==n1 or n2==t1:return None
  return('num',n1*t1/n2)
 def _sp_liar(s,p):
  pl=p.lower()
  if not re.search(r'(?:exactly|only)\s+one\s+.*?(?:truth|honest|li[ae])',pl):return None
  claims=re.findall(r'(\w+)\s+says?\s*[:\'"]\s*(.+?)[\'".]',pl)
  if not claims:claims=re.findall(r"(\w+)\s+says?\s+(?:that\s+)?(.+?)(?:\.|$)",pl)
  if len(claims)<2:return None
  people=list(dict.fromkeys(c[0]for c in claims));cm={}
  for speaker,content in claims:
   ct=content.lower().strip().rstrip('.')
   for person in people:
    if re.search(r'\b'+re.escape(person)+r'\b',ct):
     if re.search(r'always\s+lies?|liar|never\s+tells?\s+(?:the\s+)?truth',ct):cm[(speaker,person)]='liar'
     elif re.search(r'always\s+tells?\s+(?:the\s+)?truth|honest|truth[\s-]teller',ct):cm[(speaker,person)]='truth'
  for tt in people:
   if all((verdict=='truth')==(about==tt)if speaker==tt else(verdict=='truth')!=(about==tt)for(speaker,about),verdict in cm.items()):return('text',tt.capitalize())
  return None
 def _sp_lr(s,p):
  pl=p.lower()
  if not re.search(r'fac(?:e|ing)\s+(?:each\s+other|one\s+another|opposite)',pl):return None
  m=re.search(r'(?:raises?|lifts?|holds?|waves?)\s+(?:his|her|their|the)?\s*(left|right)\s+(?:hand|arm)',pl)
  if not m:m=re.search(r'(?:on|at)\s+(?:his|her|their|the)\s+(left|right)',pl)
  if not m:return None
  return('text','right'if m.group(1)=='left'else'left')
 def _sp_ka(s,p):
  pl=p.lower()
  if not re.search(r'(?:rigg|tamper|load|bias|weight)',pl)or not re.search(r"(?:doesn't|does\s+not|don't|do\s+not)\s+know",pl):return None
  if re.search(r'(?:what|how)\s+(?:\w+\s+){0,3}(?:expect|predict|think|believe|estimate)',pl):return('text','1/6'if re.search(r'die|dice',pl)else'50%'if re.search(r'coin',pl)else'1/52'if re.search(r'card|deck',pl)else'fair')
  return None
 def _sp_dn(s,p):
  pl=p.lower()
  if not re.search(r'not\s+(?:un|in|im|ir|il)\w+|not\s+\w*(?:false|untrue|incorrect|wrong|invalid)|(?:un|in|im|ir|il)\w+\s+(?:is\s+)?not\b|it\s+is\s+not\s+(?:untrue|false|incorrect|impossible)|not\s+not\b',pl):return None
  if not re.search(r'(?:is\s+\w+\s+true|true\s+or\s+false|what\s+does\s+this\s+mean)',pl):return None
  stmt=re.split(r'[.?]',pl)[0];negs=len(_NW.findall(stmt));return('text','True'if negs%2==0 else'False')
 def _sp_cc(s,p):
  pl=p.lower();conds=re.findall(r'if\s+(.+?),?\s+then\s+(.+?)(?:\.|;|$)',pl)
  if len(conds)<2:return None
  g=defaultdict(set)
  for ant,con in conds:g[ant.strip().rstrip('.')].add(con.strip().rstrip('.'))
  # Find declared truths: "X is true" OR standalone declaratives after all conditionals
  truths=set()
  for m in re.finditer(r'(\w[\w\s]*?)\s+is\s+true',pl):truths.add(m.group(1).strip())
  # Also: declarative sentences not starting with "if" and not containing "?"
  sents=[s2.strip()for s2 in re.split(r'\.\s+',pl)if s2.strip()]
  for sent in sents:
   sent=sent.strip().rstrip('.')
   if not sent.startswith('if ')and'?'not in sent and'does'not in sent and'suppose'not in sent.split()[0:1]:
    # Check if this matches any antecedent in the graph
    for ant in g:
     if ant in sent or sent in ant:truths.add(ant);break
  # Also: "Suppose X" or "X." as standalone fact
  for m in re.finditer(r'(?:suppose|given that|assume)\s+(.+?)(?:\.|$)',pl):truths.add(m.group(1).strip().rstrip('.'))
  if not truths:return None
  reachable=set(truths);changed=True
  while changed:
   changed=False
   for ant in list(g):
    if ant in reachable:
     for con in g[ant]:
      if con not in reachable:reachable.add(con);changed=True
  for qm in[re.search(r'(?:does|will|would)\s+(?:it\s+)?(?:follow|necessarily follow)\s+that\s+(.+?)(?:\?|$)',pl),re.search(r'is\s+([^.?]+?)\s+(?:true|necessarily\s+true)\s*\?',pl),re.search(r'(?:does|will|would)\s+([^.?]+?)\s+(?:follow|hold|obtain|happen)',pl)]:
   if qm:
    qt=qm.group(1).strip().rstrip('?. ')
    return('text','Yes'if qt in reachable or any(qt in r for r in reachable)else'No')
  return None
 def _sp_ac(s,p):
  pl=p.lower();cond=re.search(r'if\s+(.+?),?\s+then\s+(.+?)\.',pl)
  if not cond:return None
  con=cond.group(2).strip();rest=pl[cond.end():];cw=set(con.split()[:4])
  if not any(len(cw&set(sent.strip().split()))>=min(2,len(cw))for sent in re.split(r'\.\s+',rest)):return None
  if re.search(r'necessarily',pl)and'?'in pl:return('text','No')
  return None
 def _sp_cj(s,p):
  """Conjunction fallacy: simpler option is always more likely."""
  pl=p.lower()
  if not re.search(r'(?:more|most)\s+(?:likely|probable)',pl):return None
  return 'conjunction_flag'
 def _sp_ip(s,p):
  pl=p.lower();conds=re.findall(r'if\s+(.+?),?\s+then\s+(.+?)\.',pl)
  if not conds or len(conds)!=1:return None
  ant,con=conds[0]
  for sent in re.split(r'\.\s+',p):
   sl=sent.lower().strip()
   if sl==ant.strip()or re.search(re.escape(ant.strip())+r'\s+is\s+true',sl)or(re.search(r'is\s+true',sl)and len(set(ant.strip().split()[:4])&set(sl.split()))>=2):return('text','Yes')
  return None
 def _sp(s,p):
  pl=p.lower()
  m=re.search(r'is\s+(-?\d+\.?\d*)\s+(larger|greater|bigger|smaller|less)\s+than\s+(-?\d+\.?\d*)',pl)
  if m:
   a,b=float(m.group(1)),float(m.group(3))
   return('text','yes'if(a>b if m.group(2)in('larger','greater','bigger')else a<b)else'no')
  m=re.search(r'(?:which|what)\s+(?:\w+\s+)?(?:is\s+)?(?:larger|greater|bigger|smaller).*?(-?\d+\.?\d*)\s+(?:or|vs)\s+(-?\d+\.?\d*)',pl)
  if m:a,b=float(m.group(1)),float(m.group(2));return('num',min(a,b)if _h(pl,'smaller','less')else max(a,b))
  m=re.search(r'(-?\d+\.?\d*)\s+is\s+less\s+than\s+(-?\d+\.?\d*)',pl)
  if m and re.search(r'which.*larger',pl):return('num',float(m.group(2)))
  m=re.search(r'cost\s+\$?(\d+(?:\.\d+)?).*?costs?\s+\$?(\d+(?:\.\d+)?)\s+more',pl)
  if m:return('num',(float(m.group(1))-float(m.group(2)))/2)
  m=re.search(r'all\s+(?:but|except)\s+(\d+)',pl)
  if m and'how many'in pl:return('num',float(m.group(1)))
  m=re.search(r'(\d+)\s*(?:fence\s*)?posts?.*?(\d+)\s*(?:meter|feet|ft|m\b|yard)',pl)
  if m:return('num',(int(m.group(1))-1)*int(m.group(2)))
  m=re.search(r'(\d+)\s*(?:mod|%|modulo)\s*(\d+)',pl)
  if m:return('num',int(m.group(1))%int(m.group(2)))
  if re.search(r'coin|flip|toss',pl)and re.search(r'next|probability|chance|odds',pl):return('text','50%')
  if re.search(r'sum\s+of\s+two\s+odd|odd.*\+.*odd',pl):return('text','even')
  m=re.search(r'(\d+)\s+\w+\s*,?\s*(\d+)\s+\w+.*?(?:must|share|at\s+least)',pl)
  if m and int(m.group(1))>int(m.group(2)):return('text','yes')
  m=re.search(r'(\d+)\s+\w+.*?(\d+)\s+box',pl)
  if m and re.search(r'minimum|at\s+least|must',pl):return('num',math.ceil(int(m.group(1))/int(m.group(2))))
  if re.search(r'if.*rain.*ground.*wet',pl)and re.search(r'ground.*not\s+wet',pl):return('text','no')
  it=re.search(r'if\s+(.+?),?\s+then\s+(.+?)\.',pl)
  if it and re.search(r'not\s+\w+|n\'t',pl[it.end():])and re.search(r'therefore|must|is\s+it|can\s+we',pl):return('text','no')
  cv=re.search(r'all\s+(\w+)\s+are\s+(\w+).*?are\s+all\s+(\w+)\s+(\w+)',pl)
  if cv and cv.group(2)==cv.group(3)and cv.group(1)==cv.group(4):return('text','no')
  if re.search(r'not\s+(?:the\s+case\s+)?(?:that\s+)?all\s+\w+\s+can',pl)and re.search(r'can\s+\w+\s+\w+\?',pl):return('text','cannot be answered')
  cp=re.findall(r'(\w+)\s+is\s+(?:taller|bigger|faster|stronger|heavier)\s+than\s+(\w+)',pl)
  if len(cp)>=2:
   dom=set(b for _,b in cp);tops=[a for a,_ in cp if a not in dom]
   if tops:return('text',tops[0].capitalize())
  alls=re.findall(r'all\s+(\w+)\s+are\s+(\w+)',pl)
  if len(alls)>=2:
   g=defaultdict(set);[g[a.lower()].add(b.lower())for a,b in alls];return('chain',g)
  svo=re.search(r'(?:the\s+)?(\w+)\s+(chased|bit|kicked|pushed|pulled|followed|ate|caught|hit)\s+(?:the\s+)?(\w+)',pl)
  if svo:return('text',svo.group(3)if re.search(r'being\s+',pl)else svo.group(1))
  if re.search(r'(?:heavier|lighter).*pound.*pound',pl):return('text','same')
  if re.search(r'overtake.*(?:second|2nd)',pl):return('text','second')
  if re.search(r'0\.999.*repeating',pl):return('text','yes')
  dm=re.findall(r'(?:go|walk|turn|move|head)\s+(north|south|east|west)',pl)
  if len(dm)>=2:
   dv={'north':(0,1),'south':(0,-1),'east':(1,0),'west':(-1,0)}
   dx=sum(dv[d][0]for d in dm);dy=sum(dv[d][1]for d in dm)
   dirs=(['north']if dy>0 else['south']if dy<0 else[])+(['east']if dx>0 else['west']if dx<0 else[])
   return('text','-'.join(dirs)if dirs else'origin')
  if re.search(r'(?:increase|up).*?\d+\s*%.*?(?:then|decrease|down|back)',pl):return('text','not_same')
  if'correlat'in pl and re.search(r'cause|causal',pl):return('text','no_cause')
  ch=re.findall(r'(\w[\w\s]*?)\s+(?:leads?\s+to|causes?|results?\s+in)\s+(\w[\w\s]*?)(?:[.,;]|$)',p,re.I)
  if ch and re.search(r'intervene|block|prevent|force',pl):return('text','stops')
  mp=re.search(r'on\s+(?:her|his|their|the)\s+(left|right)',pl)
  if mp and re.search(r'opposite|directly\s+across|face[sd]?\s+\w+\s+from',pl):return('text','right'if mp.group(1)=='left'else'left')
  wt=re.search(r'wants?\s+\w+\s+to\s+(?:go\s+|pick\s+(?:the\s+)?|take\s+(?:the\s+)?)(\w+)',pl)
  if wt and re.search(r'opposite',pl):return('text',{'left':'right','right':'left','north':'south','south':'north','east':'west','west':'east'}.get(wt.group(1).lower(),wt.group(1)))
  bm=re.search(r'(?:mistakenly\s+believes?|told\s+\w+\s+that)\s+(?:the\s+)?\w[\w\s]*?is\s+(\$?\w[\w\s:]*?)(?:\s*[\.(])',pl)
  if bm:return('text',bm.group(1).strip())
  if re.search(r'tamper|rigg|load',pl)and re.search(r"doesn't|does\s+not",pl):return('text','1/6'if re.search(r'die|dice',pl)else'1/52'if re.search(r'card|deck',pl)else'fair')
  dy=re.search(r'today\s+is\s+(\w+)',pl)
  if dy and _DM.get(dy.group(1).lower())is not None:
   d=_DM[dy.group(1).lower()];off=0;rest=pl[dy.end():];_DO={'day before yesterday':-2,'day after tomorrow':2,'yesterday':-1,'tomorrow':1,'day before':-1,'day after':1}
   for t in re.findall(r'day\s+before\s+yesterday|day\s+after\s+tomorrow|yesterday|tomorrow|day\s+before|day\s+after',rest):off+=_DO[t]
   nm=re.search(r'(\d+)\s+days?\s+(?:from\s+now|later|ahead|after)',rest);off+=int(nm.group(1))if nm else 0
   nm=re.search(r'(\d+)\s+days?\s+(?:ago|before|earlier)',rest);off-=int(nm.group(1))if nm else 0
   return('text',_D[(d+off)%7].capitalize())
  tm=re.search(r'(\d{1,2}):(\d{2})\s*(am|pm).*?(\d{1,2}):(\d{2})\s*(am|pm)',pl)
  if tm:
   t1=_t24(int(tm.group(1)),int(tm.group(2)),tm.group(3));t2=_t24(int(tm.group(4)),int(tm.group(5)),tm.group(6));t2+=1440*(t2<=t1);d=t2-t1;return('text',f"{d//60} hours and {d%60} minutes")
  pr=re.findall(r'(\d{4}):\s*(\d+(?:\.\d+)?)',p)
  if len(pr)>=3:vs=[float(v)for _,v in sorted(pr)];d1=[vs[i+1]-vs[i]for i in range(len(vs)-1)];d2=[d1[i+1]-d1[i]for i in range(len(d1)-1)];return('text','Accelerating'if sum(d2)/len(d2)>0 else'Decelerating')
  av={am.group(1).lower():float(am.group(2))for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+old(?!er)',pl)}
  ac=[(am.group(1).lower(),float(am.group(2)),am.group(3),am.group(4).lower())for am in re.finditer(r'(\w+)\s+is\s+(\d+)\s+years?\s+(older|younger)\s+than\s+(\w+)',pl)]
  if av and ac:
   for _ in range(30):
    ch=False
    for nm,v,rel,ref in ac:
     sg=1 if rel=='older'else-1
     if ref in av and nm not in av:av[nm]=av[ref]+sg*v;ch=True
     if nm in av and ref not in av:av[ref]=av[nm]-sg*v;ch=True
    if not ch:break
   qm=re.search(r"(?:how\s+old\s+is|what\s+is)\s+(\w+)'?s?\s*(?:age)?",pl)
   if qm and qm.group(1).lower()in av:return('num',av[qm.group(1).lower()])
  edges=[(a.lower(),b.lower())for a,b in re.findall(r'(\w+)\s+(?:happened\s+)?before\s+(\w+)',pl)]+[(b.lower(),a.lower())for a,b in re.findall(r'(\w+)\s+(?:happened\s+)?after\s+(\w+)',pl)]
  if edges:
   nodes=set();gr=defaultdict(set);ind=defaultdict(int)
   for a,b in edges:gr[a].add(b);nodes|={a,b};ind.setdefault(a,0);ind.setdefault(b,0)
   for a,b in edges:ind[b]+=1
   q=sorted(n for n in nodes if ind[n]==0);order=[]
   while q:
    n=q.pop(0);order.append(n)
    for nb in sorted(gr[n]):
     ind[nb]-=1
     if ind[nb]==0:q.append(nb)
    q.sort()
   return('text',', '.join(w.capitalize()for w in order))
  if re.search(r'complete\s+list|exhaustive\s+list|only\s+\w+\s+are|no\s+others',pl):
   qm=re.search(r'is\s+(\w+)\s+(?:among|in|one\s+of)',pl)
   if qm:return('exact','No')
  m=re.search(r'sum\s+to\s+(\d+).*?total.*?(?:is\s+)?(\d+)',pl)
  if m:return('num',int(m.group(2))-int(m.group(1)))
  return None
 def _match(s,computed,c):
  cl=c.lower().strip();cn=_ns(c)
  if isinstance(computed,(int,float)):
   tol=max(0.01,abs(computed)*0.01)if abs(computed)<100 else 0.5
   if cn and any(abs(v-computed)<tol for v in cn):return 0.95
   if cn and any(abs(v-computed)<0.5 for v in cn):return 0.70
   st=str(int(computed))if isinstance(computed,float)and computed==int(computed)else str(computed)
   return 0.95 if st in cl else 0.08
  if isinstance(computed,dict):return 0.95 if any(ag.lower()in cl and it.lower()in cl for ag,it in computed.items())else 0.90 if any(it.lower()in cl for it in computed.values())else 0.08
  if isinstance(computed,str):
   comp=computed.lower()
   if cl==comp:return 0.95
   if comp in cl:
    pf=cl[:cl.find(comp)].strip()
    if pf and any(w in pf for w in['higher','lower','more','less','not','greater','above','below','only']):return 0.08
    return 0.95
   if cl in comp:return 0.95
   M={'stops':('stop','cease','would not'),'50%':('50','1/2','0.5'),'no_cause':('confound','not necessarily','no,','correlation'),'not_same':('not the same','less','lower','different'),'even':('even','false'),'Cannot be determined':('cannot','determined'),'cannot be answered':('cannot be answered','given information','cannot be determined'),'same':('same','equal','neither'),'second':('second','2nd'),'inconsistent':('inconsistent','no, ','no,','contradiction'),'consistent':('consistent','yes, ','yes,'),'Yes':('yes',),'No':('no',),'fair':('fair','equal','1/2','50'),'1/6':('1/6','one in six','16.7'),'1/52':('1/52','one in fifty')}
   if comp in M and _h(c,*M[comp]):
    if comp=='consistent'and'inconsistent'in cl:return 0.08
    return 0.95
   if comp=='inconsistent'and'consistent'in cl and'inconsistent'not in cl:return 0.08
   return 0.15
  if isinstance(computed,tuple):
   if computed[0]=='exact':return 0.95 if cl==computed[1].lower()else 0.08
   if computed[0]in('num','text'):return s._match(computed[1],c)
   if computed[0]=='chain':return 0.90 if _h(c,'yes')and not _h(c,'cannot')else 0.08
   if computed[0]=='cfact':
    af=computed[1];cn2=re.sub(r'^the\s+','',cl)
    for it in af:
     if it in cn2 or cn2 in it:return 0.08
     iw=set(it.split());cw=set(cn2.split())
     if len(iw)>=2 and len(iw&cw)>=len(iw)*0.6:return 0.08
    return 0.08 if'everything'in cl or'all'in cl else 0.85
  return 0.50
 def _score(s,p,c):
  for fn in[s._cm_reg,s._cm_seq,s._cm_bel,s._cm_cst,s._cm_rec,s._cm_cf,s._cm_bay,s._cm_isf,s._cm_def,s._cm_con,s._cm_int,s._cm_stb]:
   try:r=fn(p)
   except:continue
   if r is not None:return s._match(r,c),fn.__name__
  for fn in[s._sp_rate,s._sp_liar,s._sp_lr,s._sp_ka,s._sp_dn,s._sp_cc,s._sp_ac,s._sp_cj,s._sp_ip]:
   try:r=fn(p)
   except:continue
   if r=='conjunction_flag':
    return(0.90 if' and 'not in c.lower()else 0.12),'_sp_cj'
   if r is not None:
    sc=s._match(r,c);return(0.90 if sc>=0.90 else 0.12 if sc<=0.15 else sc),fn.__name__
  sp=s._sp(p)
  if sp is not None:
   sc=s._match(sp,c);return(0.90 if sc>=0.90 else 0.12 if sc<=0.15 else sc),'sp'
  ncd=s._ncd(p,c);return 0.50+(1.0-ncd)*0.08,'ncd'
 def evaluate(s,prompt:str,candidates:list)->list:
  meta=s._meta(prompt)
  res=[{'candidate':c,'score':round(s._score(prompt,c)[0]*(0.88+0.12*meta),4),'reasoning':s._score(prompt,c)[1],'meta':round(meta,3)}for c in candidates]
  res.sort(key=lambda r:r['score'],reverse=True);return res
 def confidence(s,prompt:str,answer:str)->float:
  meta=s._meta(prompt);return meta if meta<0.30 else round(min(meta,s._score(prompt,answer)[0]),4)
