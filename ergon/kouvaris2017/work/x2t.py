import sys,re,html
sys.stdout.reconfigure(encoding='utf-8')
import xml.etree.ElementTree as ET
p=sys.argv[1]
try:
    t=ET.parse(p); r=t.getroot()
except Exception as e:
    print('PARSEFAIL',e); raise SystemExit
def txt(e):
    return ''.join(e.itertext())
out=[]
for sec in r.iter():
    pass
body=r.find('.//body')
if body is None: body=r
print(re.sub(r'\n{3,}','\n\n',' '.join(txt(body).split())))
