from collections import Counter

def analyze(fn):
    data=list(map(int,open(fn).read().split()))
    it=iter(data)
    N,S,L=next(it),next(it),next(it)
    M,K,P=next(it),next(it),next(it)
    print('file',fn,'N',N,'S',S,'L',L,'M',M,'K',K,'P',P)
    for qi in range(5):
        Q=next(it)
        cnt=Counter(); deg=[0]*N
        for _ in range(Q):
            gA=next(it); la=next(it); gB=next(it); lb=next(it)
            if gA>gB: gA,gB=gB,gA
            cnt[(gA,gB)] += 1
            deg[gA]+=1; deg[gB]+=1
        vals=sorted(cnt.values())
        print(' q',qi,'Q',Q,'pairs',len(cnt),'min',vals[0],'max',vals[-1],'avg',Q/len(cnt))
        print('  deg min',min(deg),'max',max(deg),'avg',sum(deg)/N)

analyze('tests/04')
analyze('tests/05')
