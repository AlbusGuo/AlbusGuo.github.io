"""Actual radical subspaces and finite-field submodule lattices at middle zero."""
import json
from itertools import combinations
from pathlib import Path
from 六种全旗表示模型 import full_model
from 特殊线性超群根基计算 import radical_profile,dual_module,rref,submodule


def vp(n,p):
    if not n:return 10**6
    result=0
    while n%p==0:n//=p;result+=1
    return result


def unit(n,i):return tuple(int(i==j) for j in range(n))


def proposed(p,r,depth):
    q=p**r;P=q//p;n=4*q
    if depth<=r:
        indices=[4*i+e for i in range(q) for e in range(4) if e or i%p]
        indices += [4*p*j for j in range(P) if (0 if j==0 else r-1-vp(j,p))>=depth]
    else:
        indices=[4*(p*(j+1)-1)+3 for j in range(P) if vp(j+1,p)>=depth-r-1]
    return [unit(n,i) for i in sorted(indices)]


def cyclic(m,vector,p):
    pivots={};queue=[];n=m['dim']
    def add(row):
        row=[x%p for x in row]
        for pivot,old in sorted(pivots.items()):
            if row[pivot]:
                c=row[pivot];row=[(x-c*y)%p for x,y in zip(row,old)]
        pivot=next((i for i,c in enumerate(row) if c),None)
        if pivot is None:return
        inverse=pow(row[pivot],-1,p);row=[x*inverse%p for x in row]
        pivots[pivot]=row;queue.append(row)
    add(vector)
    cursor=0
    while cursor<len(queue):
        vector=queue[cursor];cursor+=1
        for matrix in m['actions']:
            image=[0]*n
            for i,c in enumerate(vector):
                if c:
                    for j,v in matrix[i].items():image[j]=(image[j]+c*v)%p
            add(image)
    return tuple(map(tuple,rref(list(pivots.values()),n,p)[0]))


def lattice(p,r,forget):
    m=full_model('132',p,r,0,0);q=p**r;n=4*q
    groups={}
    for i,(a,b,e) in enumerate(m['weights']):
        w=(a%q,b%q,e) if forget else (a,b,e)
        groups.setdefault(w,[]).append(i)
    spaces={()}
    for indices in groups.values():
        assert len(indices)<=2
        coefficients=[(1,)] if len(indices)==1 else [(1,c) for c in range(p)]+[(0,1)]
        for coefficients_row in coefficients:
            v=[0]*n
            for i,c in zip(indices,coefficients_row):v[i]=c
            spaces.add(cyclic(m,v,p))
    changed=True
    while changed:
        changed=False
        for a,b in combinations(list(spaces),2):
            joined=tuple(map(tuple,rref(list(a)+list(b),n,p)[0]))
            if joined not in spaces:spaces.add(joined);changed=True
    candidates={tuple(proposed(p,r,j)) for j in range(2*r+2)}
    V=[unit(n,4*i+e) for i in range(q) for e in [2,3]]
    W=[unit(n,4*i+1) for i in range(q)]
    for i in range(q):
        row=list(unit(n,4*i+3))
        if i+1<q:row[4*(i+1)]=-(i+1)%p
        W.append(tuple(row))
    candidates.add(tuple(map(tuple,rref(V,n,p)[0])))
    candidates.add(tuple(map(tuple,rref(W,n,p)[0])))
    assert len(spaces)==2*r+4
    assert spaces==candidates
    return dict(p=p,r=r,forget_T=forget,submodules=len(spaces),status='passed')


def main():
    profiles=[]
    for p,r in [(3,1),(3,2),(3,3),(5,1),(5,2)]:
        m=full_model('132',p,r,0,0)
        dims,heads,embeddings=radical_profile(m,p,r,with_embeddings=True)
        assert len(dims)==2*r+2
        for j,basis in enumerate(embeddings):
            assert rref(basis,m['dim'],p)[0]==[list(v) for v in proposed(p,r,j)],(p,r,j)
        dualdims,_=radical_profile(dual_module(m,p,r),p,r)
        assert dualdims==dims
        profiles.append(dict(p=p,r=r,radical_dimensions=dims,actual_subspaces='passed',dual_dimensions='passed'))
        print(json.dumps(profiles[-1]),flush=True)
    lattices=[lattice(p,r,forget) for p,r in [(3,1),(3,2),(5,1)] for forget in [False,True]]
    result={'status':'passed','profiles':profiles,'lattices':lattices,
            'lattice_scope':'Exhaustive over the prime field, by generating all homogeneous weight lines and closing under sums; the general algebraically closed-field claim uses the proof.'}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/中间零权子模格核验结果.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
