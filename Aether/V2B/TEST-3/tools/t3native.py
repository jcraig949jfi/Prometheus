import os,subprocess,sys,time
PIN=r"C:/Prometheus-worktrees/aether-v2b-t3"; D=r"C:/Prometheus-data/aether/V2B/TEST-3/native"
os.makedirs(D,exist_ok=True)
env=dict(os.environ,OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1")
P1=[(l,"on") for l in ("mob_r0x1e0","mob_r0x1e1","mob_r1x0e0","mob_r1x0e1","mob_r1x1e0","mob_r1x1e1")]+[("v1","off")]
units=[("T3-P1-%s-w%s-s%d"%(l,w,s),"aeth_mobility.py",["--law",l,"--seed-index",str(s),"--arm","off","--warmup-arm",w]) for l,w in P1 for s in (4,5,6,7)]
units+=[("T3-P3-%s-s%d"%(l,s),"aeth_prov_assay.py",["--law",l,"--seed-index",str(s),"--arm","off"]) for l in ("mob_r1x1e0","mob_r1x1e1") for s in (4,5,6,7)]
if len(sys.argv)>1 and sys.argv[1]=="dup":
    uid,script,args=units[int(sys.argv[2])]; out=os.path.join(D,"dup_%s.json"%uid)
    rc=subprocess.call([sys.executable,"Aether/observatory/"+script]+args+["--out",out],cwd=PIN,env=env); print(uid,"dup rc",rc); sys.exit(rc)
done=lambda u: os.path.exists(os.path.join(D,"t3_%s.json"%u[0]))
todo=[u for u in units if not done(u)]
deadline=time.time()+470
while todo and time.time()<deadline:
    wave,todo=todo[:3],todo[3:]; procs=[]
    for uid,script,args in wave:
        out=os.path.join(D,"t3_%s.json"%uid)
        lf=open(os.path.join(D,uid+".stdout"),"w"); ef=open(os.path.join(D,uid+".stderr"),"w")
        p=subprocess.Popen([sys.executable,"Aether/observatory/"+script]+args+["--out",out+".part"],cwd=PIN,env=env,stdout=lf,stderr=ef)
        procs.append((uid,p,out,lf,ef,time.time()))
    for uid,p,out,lf,ef,t0 in procs:
        rc=p.wait(); lf.close(); ef.close()
        if rc==0: os.replace(out+".part",out)
        print(uid,"rc",rc,"wall",round(time.time()-t0,1),flush=True)
print("remaining",len([u for u in units if not done(u)]),"of",len(units))
