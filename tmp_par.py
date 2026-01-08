from collections import Counter

def parity_stats(fn, qi):
    data=list(map(int,open(fn).read().split()))
    it=iter(data)
    N,S,L=next(it),next(it),next(it)
    M,K,P=next(it),next(it),next(it)
    for q in range(5):
        Q=next(it)
        same=0; diff=0
        for _ in range(Q):
            gA=next(it); la=next(it); gB=next(it); lb=next(it)
            if (gA^gB)&1: diff+=1
            else: same+=1
        if q==qi:
            print(fn,'q',qi,'sameParity',same,'diffParity',diff)
            return

parity_stats('tests/04',0)
parity_stats('tests/04',1)
parity_stats('tests/05',0)
parity_stats('tests/05',1)
