from collections import Counter

def analyze_leaves(fn, qi_target):
    data=list(map(int,open(fn).read().split()))
    it=iter(data)
    N,S,L=next(it),next(it),next(it)
    M,K,P=next(it),next(it),next(it)
    for qi in range(5):
        Q=next(it)
        flows=[]
        for _ in range(Q):
            gA=next(it); la=next(it); gB=next(it); lb=next(it)
            flows.append((gA,la,gB,lb))
        if qi==qi_target:
            deg=[0]*(N*L)
            for gA,la,gB,lb in flows:
                deg[gA*L+la]+=1
                deg[gB*L+lb]+=1
            mx=max(deg); mn=min(deg); avg=sum(deg)/(N*L)
            cnt=Counter(deg)
            print(fn,'q',qi,'Q',Q,'leafdeg min',mn,'max',mx,'avg',avg)
            for d in sorted(cnt)[:10]:
                print(' ',d,cnt[d])
            if len(cnt)>10:
                print(' ...')
            for d in sorted(cnt)[-10:]:
                if d in sorted(cnt)[:10]:
                    continue
                print(' ',d,cnt[d])
            break

for fn in ['tests/04','tests/05']:
    for qi in [0,1,3]:
        analyze_leaves(fn, qi)
