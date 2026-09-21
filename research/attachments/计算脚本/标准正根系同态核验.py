"""Primitive vectors and ranks of all standard-Borel baby-Verma maps.

The prediction is compared to independent simultaneous positive-generator kernels.
"""
from pathlib import Path
from math import prod
import json
from 特殊线性超群环境配对核验 import act
from 特殊线性超群根基计算 import weight,rref
from 秩一同态核验 import digits,height


def primitive(m,n,p):
    return n==0 or (m-n+1)%p**height(n,p)==0


def predictions(p,r,a,b):
    q=p**r
    out=[]
    def add(kind,n,v):
        v={i:c%p for i,c in v.items() if c%p}
        assert v
        out.append({'kind':kind,'index':n,'vector':v,'weight':weight(next(iter(v)),a,b)})
    for i in range(q):
        if primitive(a,i,p):
            add('V',i,{4*i:1})
            if b%p==0 and (i+1)%p==0:add('C',i,{4*i+3:1})
    if b%p==0:
        for j in range(q):
            if primitive(a+1,j,p):
                add('W',j,{4*j+2:1,**({4*(j-1)+1:-1} if j else {})})
        if (a+1)%p==0:
            for j in range(p,q,p):
                if primitive(a,j,p):add('T',j,{4*j+2:1})
    elif (a+b+1)%p==0:
        for i in range(q):
            if primitive(a-1,i,p):
                add('Z',i,{4*i+1:a-i,**({4*(i+1)+2:i+1} if i+1<q else {})})
    return out


def predicted_rank(row,p,r,a):
    n=row['index']
    ds=digits(n,p,r)
    R=prod(p-x for x in ds)
    if row['kind']=='V':return 4*R
    if row['kind']=='C':return R
    if row['kind'] in ['W','T']:
        if n==0:return 2*p**r
        nu=next(j for j,x in enumerate(ds) if x)
        H=prod(p-x for x in ds[nu+1:])
        return 2*R+H
    if n==0 and a%p!=0:return 2*p**r
    return (2*p-2*ds[0]-1)*prod(p-x for x in ds[1:])


def image_vector(op,s,vector,a,b,p,q):
    out={}
    for i,c in vector.items():
        for j,x in act(op,s,i,a,b).items():out[j]=(out.get(j,0)+c*x)%p
    out={j:c for j,c in out.items() if c}
    assert all(j<4*q for j in out)
    return out


def image_rank(vector,p,r,a,b):
    q=p**r
    pivots={}
    for n in range(q):
        v=image_vector('F',n,vector,a,b,p,q)
        y1=image_vector('y1',1,v,a,b,p,q)
        y2=image_vector('y2',1,v,a,b,p,q)
        both=image_vector('y1',1,y2,a,b,p,q)
        for candidate in [v,y1,y2,both]:
            row=dict(candidate)
            while row:
                j=min(row)
                if j not in pivots:
                    inv=pow(row[j],-1,p)
                    pivots[j]={k:c*inv%p for k,c in row.items()}
                    break
                c=row[j]
                for k,x in pivots[j].items():
                    row[k]=(row.get(k,0)-c*x)%p
                    if not row[k]:del row[k]
    return len(pivots)


def check(p,r,a,b,check_rank):
    q=p**r
    predicted=predictions(p,r,a,b)
    by_weight={}
    for row in predicted:
        assert row['weight'] not in by_weight
        by_weight[row['weight']]=row
    groups={}
    for i in range(4*q):groups.setdefault(weight(i,a,b),[]).append(i)
    positive=[('E',p**j) for j in range(r)]+[('x1',1),('x2',1)]
    aa,bb=a+q,b+q
    actual_count=0
    residues=set()
    for w,indices in groups.items():
        equations=[]
        for op,s in positive:
            eq={}
            for col,i in enumerate(indices):
                for j,c in act(op,s,i,aa,bb).items():
                    if c%p:eq.setdefault(j,[0]*len(indices))[col]=c%p
            equations.extend(eq.values())
        rr,pivots=rref(equations,len(indices),p)
        dim=len(indices)-len(pivots)
        assert dim==int(w in by_weight),(p,r,a,b,w,dim,by_weight.get(w))
        if dim:
            row=by_weight[w]
            coords=[row['vector'].get(i,0) for i in indices]
            assert all(sum(c*x for c,x in zip(eq,coords))%p==0 for eq in equations)
            residue=(w[0]%q,w[1]%q)
            assert residue not in residues,('ungraded-torus collision',p,r,a,b,w)
            residues.add(residue)
            actual_count+=1
    if check_rank:
        for row in predicted:
            got=image_rank(row['vector'],p,r,aa,bb)
            want=predicted_rank(row,p,r,a)
            assert got==want,('rank',p,r,a,b,row,got,want)
    return len(groups),actual_count,len(predicted) if check_rank else 0,predicted


def main():
    counts={'modules':0,'weight_spaces':0,'primitive_vectors':0,'map_ranks':0}
    examples=[]
    for p,maxr in [(3,4),(5,3),(7,2)]:
        for r in range(1,maxr+1):
            q=p**r
            for a in range(q):
                for b in range(p):
                    ranks=q<=49 or (a,b) in [(q//p-1,0),(q-2,0)]
                    n,v,k,pred=check(p,r,a,b,ranks)
                    counts['modules']+=1;counts['weight_spaces']+=n
                    counts['primitive_vectors']+=v;counts['map_ranks']+=k
                    if (p,r,a,b) in [(3,2,0,0),(3,2,2,0),(3,2,1,1),(3,2,8,0)]:
                        examples.append({'p':p,'r':r,'target_weight':[a,b],
                                         'maps':[{key:row[key] for key in ['kind','index','weight']}|{'rank':predicted_rank(row,p,r,a)} for row in pred]})
    result={'status':'passed','scope':'Positive-generator kernels and independently generated negative-PBW image ranks.',
            **counts,'examples':examples}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/标准同态分类核验结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
