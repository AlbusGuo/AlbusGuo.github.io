"""Check the all two-wall middle-Borel radical formula as actual subspaces."""
import json
from pathlib import Path
from 秩一同态核验 import choose
from 中间正根系整环境核验 import lift,v
from 六种全旗表示模型 import full_model
from 特殊线性超群根基计算 import radical_profile,dual_module,rref


def depths(p,r,a):
    q=p**r;s=min(v(a,p),r)
    assert s>=1
    bp=0 if s==r else p**s*next(t for t in range(1,p) if (a//p**s+t)%p)
    A,B=lift(p,r,a,bp)
    eta=[v(choose(A-1,i),p) for i in range(q)]
    out=[]
    for i in range(q):
        out.extend([v(choose(A,i),p),s+eta[i],s+eta[i],r+s if i==q-1 else s+v(i+1,p)+eta[i+1]])
    return out


def main():
    cases=[(3,1,0,0),(3,2,0,0),(3,2,3,0),(3,2,6,0),(3,2,3,3)]
    cases += [(3,3,a,0) for a in [3,6,9,12,18,24]]
    cases += [(5,2,a,0) for a in [5,10,15,20]]
    result=[]
    for p,r,a,b in cases:
        m=full_model('132',p,r,a,b);d=depths(p,r,a);L=r+min(v(a,p),r)+1
        dims,heads,bases=radical_profile(m,p,r,with_embeddings=True)
        assert len(dims)==L+1
        for j,rows in enumerate(bases):
            proposed=[[int(i==k) for k in range(m['dim'])] for i,degree in enumerate(d) if degree>=j]
            assert rref(rows,m['dim'],p)[0]==proposed,(p,r,a,b,j)
        dualdims,_=radical_profile(dual_module(m,p,r),p,r)
        layers=[x-y for x,y in zip(dims,dims[1:])]
        duallayers=[x-y for x,y in zip(dualdims,dualdims[1:])]
        assert duallayers==layers[::-1]
        result.append({'p':p,'r':r,'a':a,'b':b,'radical_dimensions':dims,
                       'actual_subspaces':'passed','reversed_dual_layers':'passed'})
        print(json.dumps(result[-1]),flush=True)
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/中间全权根基核验结果.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
