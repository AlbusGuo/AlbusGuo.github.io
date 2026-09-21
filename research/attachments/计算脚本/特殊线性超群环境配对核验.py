"""Exact integral checks for the sl(2|1) finite Kac lattice and its pairing."""
from math import comb, prod
from pathlib import Path
import json


def C(n,s):
    return comb(n,s) if 0<=s<=n else 0


def act(op,s,index,a,b):
    i,eps=divmod(index,4)
    result={}
    def add(j,e,c):
        if 0<=j<=a and c:
            idx=4*j+e
            result[idx]=result.get(idx,0)+c
    if op=='F':
        add(i+s,eps,C(i+s,s))
        if eps==2:
            add(i+s-1,1,-C(i+s-1,s-1))
    elif op=='E':
        add(i-s,eps,C(a-i+s,s))
        if eps==1:
            add(i-s+1,2,-C(a-i+s-1,s-1))
    elif op=='y1':
        if eps==0: add(i,1,1)
        if eps==2: add(i,3,1)
    elif op=='y2':
        if eps==0: add(i,2,1)
        if eps==1: add(i,3,-1)
    elif op=='x1':
        if eps==1: add(i,0,a+b-i)
        if eps==2: add(i-1,0,a-i+1)
        if eps==3:
            add(i,2,a+b-i+1)
            add(i-1,1,-(a-i+1))
    elif op=='x2':
        if eps==1: add(i+1,0,i+1)
        if eps==2: add(i,0,b+i)
        if eps==3:
            add(i+1,2,i+1)
            add(i,1,-(b+i+1))
    elif op=='h1':
        add(i,eps,a-2*i-(eps&1)+((eps>>1)&1))
    elif op=='h2':
        add(i,eps,b+i+(eps&1))
    return {j:c for j,c in result.items() if c}


def form(i,j,a,b):
    k,ep=divmod(i,4)
    l,fp=divmod(j,4)
    if i==j:
        return [1,a+b-k,b+k,b*(a+b+1)][ep]*C(a,k)
    if ep==1 and fp==2 and l==k+1:
        return (a-k)*C(a,k)
    if ep==2 and fp==1 and k==l+1:
        return (a-l)*C(a,l)
    return 0


def val(n,p):
    if n==0:
        return 100000
    v=0
    while n%p==0:
        v+=1
        n//=p
    return v


def apply_to(op,vector,a,b):
    out={}
    for i,c in vector.items():
        for j,d in act(op,1,i,a,b).items():
            out[j]=out.get(j,0)+c*d
    return {j:c for j,c in out.items() if c}


def check_integral(a,b):
    ops=['E','F','h1','h2','x1','x2','y1','y2']
    theta={'E':'F','F':'E','h1':'h1','h2':'h2','x1':'y1','y1':'x1','x2':'y2','y2':'x2'}
    n=4*(a+1)
    for op in ops:
        for i in range(n):
            lhsvec=act(op,1,i,a,b)
            for j in range(n):
                lhs=sum(c*form(v,j,a,b) for v,c in lhsvec.items())
                rhs=sum(c*form(i,v,a,b) for v,c in act(theta[op],1,j,a,b).items())
                assert lhs==rhs,('pairing',a,b,op,i,j,lhs,rhs)
    # Key Lie super brackets independently checked on the explicit matrices.
    relations=[('E','F',0,{'h1':1}),('x1','y1',1,{'h1':1,'h2':1}),
               ('x2','y2',1,{'h2':1}),('x1','y2',1,{'E':1}),
               ('x2','y1',1,{'F':1}),('x1','x2',1,{}),('y1','y2',1,{})]
    for x,y,odd,rhsops in relations:
        for i in range(n):
            lhs=apply_to(x,act(y,1,i,a,b),a,b)
            second=apply_to(y,act(x,1,i,a,b),a,b)
            for j,c in second.items(): lhs[j]=lhs.get(j,0)-(-1)**odd*c
            rhs={}
            for op,c in rhsops.items():
                for j,v in act(op,1,i,a,b).items(): rhs[j]=rhs.get(j,0)+c*v
            assert {j:c for j,c in lhs.items() if c}=={j:c for j,c in rhs.items() if c},('bracket',a,b,x,y,i)
    for x in ['x1','x2','y1','y2']:
        for i in range(n):
            assert not apply_to(x,act(x,1,i,a,b),a,b)
    for i in range(a+1):
        result=apply_to('x2',act('x1',1,4*i+3,a,b),a,b)
        assert result=={4*i:b*(a+b+1)}


def choose_lift(p,r,d,e):
    q=p**r
    for t in range(1,p+1):
        a,b=d+q,e+t*q
        if val(b,p)==min(val(e,p),r) and val(a+b+1,p)==min(val(d+e+1,p),r):
            return a,b
    raise AssertionError('no lift')


def block_data(a,b,i,p):
    g11=(a+b-i)*C(a,i)
    g22=(b+i+1)*C(a,i+1)
    g12=(a-i)*C(a,i)
    s=min(val(g11,p),val(g22,p),val(g12,p))
    t=val(g11*g22-g12*g12,p)-s
    line=None
    if t>s:
        aa,bb,cc=(g11//p**s)%p,(g12//p**s)%p,(g22//p**s)%p
        line=((-bb)%p,aa) if aa else (cc,(-bb)%p)
        assert any(line)
        assert (aa*line[0]+bb*line[1])%p==0 and (bb*line[0]+cc*line[1])%p==0
    return s,t,line


def check_layers(p,r,d,e,a,b,us,vb,vc,last):
    q=p**r
    ops=[(x,1) for x in ['x1','x2','y1','y2']]+[(x,p**j) for x in ['E','F'] for j in range(r)]
    for k in range(1,2*r+2):
        basis=[]
        for i,u in enumerate(us):
            if u>=k: basis.append({4*i:1})
            if u+vb+vc>=k: basis.append({4*i+3:1})
        if vb>=k: basis.append({2:1})
        if last>=k: basis.append({4*(q-1)+1:1})
        for i in range(q-1):
            s,t,line=block_data(a,b,i,p)
            if k<=s:
                basis.extend([{4*i+1:1},{4*(i+1)+2:1}])
            elif k<=t:
                basis.append({j:c for j,c in [(4*i+1,line[0]),(4*(i+1)+2,line[1])] if c})
        pivots={}
        for vector in basis:
            v=dict(vector)
            while v:
                j=min(v)
                if j not in pivots:
                    inv=pow(v[j],-1,p)
                    pivots[j]={u:c*inv%p for u,c in v.items()}
                    break
                scalar=v[j]
                for u,c in pivots[j].items():
                    v[u]=(v.get(u,0)-scalar*c)%p
                    if not v[u]: del v[u]
        for vector in basis:
            for op,s in ops:
                out={}
                for i,c in vector.items():
                    for j,value in act(op,s,i,a,b).items(): out[j]=(out.get(j,0)+c*value)%p
                out={j:c for j,c in out.items() if c}
                while out:
                    j=min(out)
                    assert j in pivots,('layer-not-stable',p,r,d,e,k,op,s,vector,out)
                    scalar=out[j]
                    for u,c in pivots[j].items():
                        out[u]=(out.get(u,0)-scalar*c)%p
                        if not out[u]: del out[u]


def check_family(p,r,d,e):
    q=p**r
    a,b=choose_lift(p,r,d,e)
    # The first q even PBW indices must be closed after reduction, including cross terms.
    for i in range(4*q):
        for op,s in [(x,1) for x in ['x1','x2','y1','y2']]+[(x,p**j) for x in ['E','F'] for j in range(r)]:
            assert all(j<4*q or c%p==0 for j,c in act(op,s,i,a,b).items()),('stable',p,r,d,e,op,s,i)
    vb,vc=val(b,p),val(a+b+1,p)
    norms=[val(C(a,i),p) for i in range(q)]
    exponents=norms+[u+vb+vc for u in norms]
    exponents.append(vb) # isolated y2 v0 weight
    last=norms[-1]+vc
    exponents.append(last)
    # Intersect AFTER reduction: p-multiples of the outside partner may correct a lift.
    boundary_s,boundary_t,boundary_line=block_data(a,b,q-1,p)
    actual_boundary=boundary_t if boundary_line and boundary_line[1]==0 else boundary_s
    assert last==actual_boundary,('boundary-intersection',p,r,d,e,last,actual_boundary)
    for i in range(q-1):
        g11=(a+b-i)*C(a,i)
        g22=(b+i+1)*C(a,i+1)
        g12=(a-i)*C(a,i)
        determinant=g11*g22-g12*g12
        assert determinant==b*(a+b+1)*C(a,i)*C(a,i+1)
        small=min(val(g11,p),val(g22,p),val(g12,p))
        predicted=min(norms[i]+vb,norms[i+1]+min(vb,val(i+1,p)))
        assert small==predicted
        large=val(determinant,p)-small
        assert large>=small
        exponents += [small,large]
    assert len(exponents)==4*q
    assert sum(exponents)==4*sum(norms)+2*q*(vb+vc)
    d0,e0=d%p,e%p
    low_dimension=2*d0+1 if e0==0 else (2*d0+3 if (d0+e0+1)%p==0 else 4*(d0+1))
    high_dimension=prod((d//p**j)%p+1 for j in range(1,r))
    assert sum(x==0 for x in exponents)==low_dimension*high_dimension
    if vb==vc==0:
        assert sorted(exponents)==sorted(norms*4)
    if (d,e) in [(0,0),(q-1,0),(1,1),(1,q-1),(q//2,q//2)]:
        check_layers(p,r,d,e,a,b,norms,vb,vc,last)
    return {'p':p,'r':r,'d':d,'e':e,'lift':[a,b],
            'filtration_dimensions':[sum(v>=k for v in exponents) for k in range(max(exponents)+2)],
            'weighted_sum_dimension':sum(exponents)}


def main():
    for a,b in [(3,3),(4,5),(8,6),(9,9)]:
        check_integral(a,b)
    count=0
    examples=[]
    for p,r in [(3,1),(3,2),(3,3),(5,1),(5,2)]:
        q=p**r
        for d in range(q):
            for e in range(q):
                record=check_family(p,r,d,e)
                count+=1
                if (d,e) in [(0,0),(q-1,0),(1,1)]: examples.append(record)
    result={'status':'passed','integral_pairing_and_bracket_cases':4,
            'finite_Gr_stability_and_smith_cases':count,
            'layer_stability_checked_on':'Up to five representative weight pairs in each of five (p,r) families',
            'boundary_convention':'Intersect the reduced ambient filtration; allow p-times outside-vector corrections.',
            'examples':examples}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/标准整环境配对核验结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__': main()
