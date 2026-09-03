UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
JAR=.work/jar.txt; : > $JAR
T="$1"; OUT="$2"; RM="${3:-full}"
curl -sSL --compressed --max-time 90 -A "$UA" -b $JAR -c $JAR "$T" -o .work/ch.html -w "f1 HTTP:%{http_code}\n"
export PYTHONIOENCODING=utf-8
python - "$T" "$RM" <<'EOF' > .work/sol.txt
import re,json,hashlib,sys,urllib.parse
t=open('.work/ch.html',encoding='utf-8',errors='replace').read()
m=re.search(r'<script id="anubis_challenge" type="application/json">(.*?)</script>',t,re.S)
if not m: print("NOCHALLENGE");sys.exit()
ch=json.loads(m.group(1)); rd=ch['challenge']['randomData']; diff=ch['rules']['difficulty']; cid=ch['challenge']['id']
pre="0"*diff; n=0
while True:
    h=hashlib.sha256((rd+str(n)).encode()).hexdigest()
    if h.startswith(pre): break
    n+=1
u=urllib.parse.urlparse(sys.argv[1])
redir=sys.argv[1] if sys.argv[2]=="full" else u.path+(("?"+u.query) if u.query else "")
print(cid);print(h);print(n);print(redir);print("https://"+u.netloc)
EOF
CID=$(sed -n 1p .work/sol.txt); H=$(sed -n 2p .work/sol.txt); N=$(sed -n 3p .work/sol.txt); R=$(sed -n 4p .work/sol.txt); HO=$(sed -n 5p .work/sol.txt)
echo "id=$CID nonce=$N"
curl -sSL --compressed --max-time 90 -A "$UA" -b $JAR -c $JAR -G --data-urlencode "id=$CID" --data-urlencode "response=$H" --data-urlencode "nonce=$N" --data-urlencode "redir=$R" --data-urlencode "elapsedTime=3000" "$HO/.within.website/x/cmd/anubis/api/pass-challenge" -o "$OUT" -w "pass HTTP:%{http_code} SIZE:%{size_download} TYPE:%{content_type}\n"
curl -sSL --compressed --max-time 90 -A "$UA" -b $JAR -c $JAR "$T" -o "$OUT" -w "f2 HTTP:%{http_code} SIZE:%{size_download} TYPE:%{content_type}\n"
