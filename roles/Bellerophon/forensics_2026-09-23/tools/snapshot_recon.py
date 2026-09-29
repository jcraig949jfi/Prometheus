import json, collections
W='C:/Users/James/z80atlas_campaign_2026-09-19/'
fl=json.load(open(W+'flags.json'))
for n in (15,108,169,446,len(fl)):
    print('first',n,'flags:',dict(collections.Counter(f['flag'] for f in fl[:n])))
cks={1060,10084,15556,15583,15585,37732,63247}
sp=0; trig=collections.Counter(); unseeded=0
with open(W+'runs.jsonl') as f:
    for i,l in enumerate(f,1):
        r=json.loads(l)
        if r.get('triggers',{}).get('spontaneous_replication'): sp+=1
        fr=r.get('first_replication')
        if fr and fr.get('seeded') is False: unseeded+=1
        if i in cks: print('runs.jsonl lines',i,'spontaneous_replication trigger',sp,'unseeded first_replication',unseeded)
print('total lines',i)
