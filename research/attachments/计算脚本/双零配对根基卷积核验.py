"""Compare proposed convolution SUBSPACES with independent Hom-derived radicals."""
from pathlib import Path
import json
from 特殊线性超群根基计算 import baby,radical_profile,rref
from 特殊线性超群环境配对核验 import val,choose_lift,block_data,C


def convolution_basis(p,r,a,n):
    q=p**r
    d=a%q
    s=min(val(d+1,p),r)
    low=p**s
    high=q//low
    highest=(d-(low-1))//low
    rows=[]
    for j in range(high):
        depth=val(C(highest+high,j),p)
        k=n-depth
        def add(terms):
            row=[0]*(4*q)
            for i,e,c in terms:
                row[4*(low*j+i)+e]=c%p
            rows.append(row)
        if k<=0:
            for i in range(low):
                for e in range(4):add([(i,e,1)])
        elif k<=2*s:
            for i in range(low):add([(i,3,1)])
            for i in range(low):
                if k<=s or i%p**(2*s-k+1):
                    add([(i,2,1)]+([(i-1,1,-1)] if i else []))
            if k<=s:
                for i in range(low):
                    if (i+1)%p**k==0:add([(i,1,1)])
    return rref(rows,4*q,p)[0]


def ambient_basis(p,r,a,b,n):
    q=p**r
    d,e=a%q,b%q
    aa,bb=choose_lift(p,r,d,e)
    vb,vc=val(bb,p),val(aa+bb+1,p)
    rows=[]
    def add(items):
        row=[0]*(4*q)
        for i,c in items:row[i]=c%p
        rows.append(row)
    for i in range(q):
        u=val(C(aa,i),p)
        if u>=n:add([(4*i,1)])
        if u+vb+vc>=n:add([(4*i+3,1)])
    if vb>=n:add([(2,1)])
    if val(C(aa,q-1),p)+vc>=n:add([(4*(q-1)+1,1)])
    for i in range(q-1):
        s,t,line=block_data(aa,bb,i,p)
        if n<=s:
            add([(4*i+1,1)]);add([(4*(i+1)+2,1)])
        elif n<=t:
            add([(4*i+1,line[0]),(4*(i+1)+2,line[1])])
    return rref(rows,4*q,p)[0]


def main():
    cases=[(3,2,a,b) for a in [2,5,8] for b in [0,3,6]]
    cases += [(3,3,2,0),(3,3,2,3),(3,3,8,0),(3,3,8,9),(5,2,4,5),(5,2,9,5)]
    results=[]
    root=Path(__file__).resolve().parents[1]
    target=root/'核验数据/双零配对卷积核验结果.json'
    for p,r,a,b in cases:
        module=baby(p,r,a,b)
        rd,heads,embeddings=radical_profile(module,p,r,True)
        s=min(val(a+1,p),r)
        assert len(rd)-1==r+s+1
        for n,actual in enumerate(embeddings):
            assert convolution_basis(p,r,a,n)==actual,('convolution',p,r,a,b,n)
        hb,hc=min(val(b,p),r),min(val(a+b+1,p),r)
        same=all(ambient_basis(p,r,a,b,n)==convolution_basis(p,r,a,n) for n in range(2*r+2))
        assert same==(hb==hc==s),('equality criterion',p,r,a,b,hb,hc,s)
        result={'p':p,'r':r,'weight':[a,b],'s':s,'radical_dimensions':rd,
                'actual_subspaces_match_convolution':True,'pairing_equals_radical':same,
                'odd_valuations':[hb,hc]}
        results.append(result)
        target.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__=='__main__':main()
