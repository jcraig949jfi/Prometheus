L=open('prompts_cls.py',encoding='utf-8').read().split('\n')
B=chr(92)+'b'; W=chr(92)+'w*'
L[23]="    r['f_correct']=bool(re.search(r\"%s(wrong|mistake|incorrect|misread|overclaim|not what i|you did not|you didn't|that is not|stop (doing|running|launching)|do not repeat|violat%s|error)%s\",t))"%(B,W,B)
L[24]="    r['f_unblock']=bool(re.search(r\"%s(unblock%s|blocked|go ahead|you may (now )?proceed|proceed|released?|lift(ed)? the hold)%s\",t))"%(B,W,B)
L[25]="    r['f_gate']=bool(re.search(r\"%s(approv%s|authoriz%s|go|sign-?off|accepted)%s\",t))"%(B,W,W,B)
L[26]="    r['f_infra']=bool(re.search(r\"%s(lease|heartbeat|machine|m1|m2|m4|fabric|comms|cpu|gpu|workers?|install)%s\",t))"%(B,B)
open('prompts_cls.py','w',encoding='utf-8').write('\n'.join(L))
